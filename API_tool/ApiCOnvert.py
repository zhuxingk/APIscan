import re
from bs4 import BeautifulSoup


class MarkdowntoSql:
    def __init__(self, md_file, sql_file):
        self.md_file = md_file
        self.sql_file = sql_file
        self.sql_list = []

    def parse_markdown(self):
        with open(self.md_file, encoding='utf-8') as f:
            md = f.read()

        # 解析markdown表格
        soup = BeautifulSoup(md, 'html.parser')
        tables = soup.find_all('table')

        for table in tables:
            headers = [header.get_text() for header in table.find_all('th')]
            rows = table.find_all('tr')
            for row in rows:
                values = [value.get_text().strip() for value in row.find_all('td')]
                if len(headers) == len(values):
                    # 根据解析到的值生成sql语句
                    self.sql_list.append(self.generate_sql(headers, values))

        # 解析markdown标题和内容
        sections = re.findall('##\s(.*?)\n([\s\S]*?)(?=##\s|$)', md)

        for title, content in sections:
            url = ''
            method = ''
            request = ''
            response_true = ''
            response_false = ''

            # 解析每个section的内容
            lines = content.split('\n')
            for line in lines:
                if line.startswith('- URL:'):
                    url = line.replace('- URL:', '').strip()
                elif line.startswith('- Method:'):
                    method = line.replace('- Method:', '').strip()
                elif line.startswith('- Request:'):
                    request = self.parse_json(lines, 'Request')
                elif line.startswith('- Response(TRUE):'):
                    response_true = self.parse_json(lines, 'Response(TRUE)')
                elif line.startswith('- Response(FALSE):'):
                    response_false = self.parse_json(lines, 'Response(FALSE)')

            # 根据解析到的值生成sql语句
            self.sql_list.append(self.generate_sql(title, url, method, request, response_true, response_false))
            print(self.sql_list)

    def generate_sql(self, *args):
        sql = "INSERT INTO `api` ("
        for arg in args:
            if type(arg) == str:
                sql += "`title`, "
            elif type(arg) == list:
                for item in arg:
                    sql += f"`{item}`, "
            else:
                sql += "`url`, `method`, `request`, `response_true`, `response_false`, "
                break
        sql = sql[:-2] + ") VALUES ("
        for arg in args:
            if type(arg) == str:
                sql += f"'{arg}', "
            elif type(arg) == list:
                sql += f"'{','.join(arg)}', "
            else:
                sql += f"'{arg}', "
        sql = sql[:-2] + ");\n"
        return sql

    # def generate_sql(self, *args):
    #     sql = "INSERT INTO `api` ("
    #     for arg in args:
    #         if type(arg) == str:
    #             sql += "`title`, "
    #         elif type(arg) == list:
    #             for item in arg:
    #                 sql += f"`{item}`, "
    #         else:
    #             sql += "`url`, `method`, `request`, `response_true`, `response_false`"
    #             break
    #     sql = sql[:-2] + ") VALUES ("
    #     for arg in args:
    #         if type(arg) == str:
    #             sql += f"'{arg}', "
    #         elif type(arg) == list:
    #             sql += f"'{','.join(arg)}', "
    #         else:
    #             sql += f"'{arg}', "
    #     sql = sql[:-2] + ");\n"
    #     return sql

    def parse_json(self, lines, start):
        result = ''
        flag = False
        for line in lines:
            if line.startswith(f'- {start}:'):
                result += line.replace(f'- {start}:', '').strip()
                flag = True
            elif flag and line.startswith('- '):
                result += '\n' + line[2:].strip()
            else:
                break
        return result

    def decode_sql(self):
        self.parse_markdown()

        if not self.sql_list:
            raise Exception('No SQL generated from the markdown file')

        with open(self.sql_file, 'w', encoding='utf-8') as f:

            for sql in self.sql_list:
                f.write(sql)
if __name__ == '__main__':
    md_file = './test.md'
    sql_file = './test.sql'
    MarkdowntoSql(md_file, sql_file).decode_sql()