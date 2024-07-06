"""
ARCHIVO PARA ANALIZAR UN FICHERO

"""

import sys
import subprocess
import re
import pyodbc
from datetime import datetime

SERVER = 'LAPTOP-E26LIVT1\\SQLEXPRESS'
DATABASE = 'NUEVO'
TABLE = 'Code'
TABLE_FOREIGN = 'Files'


class struct:
    pass


def parse_chunk_header(s):
    Chunk_Header_Pat = re.compile('@@ -([0-9]+)(?:,([0-9]+))? \\+([0-9]+)(?:,([0-9]+))? @@')
    origL, del_N, newL, add_N = Chunk_Header_Pat.match(s).groups()
    if del_N is None:
        del_N = 1
    if add_N is None:
        add_N = 1
    return list(map(int, (origL, del_N, newL, add_N)))


def get_initial_version(first_rev, fn):
    lines = []
    file_started_FL = False
    cmd = ['git', 'show', '%s' % first_rev, fn]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return lines
    except UnicodeDecodeError as e:
        print(f"Error decoding output: {e}")
        return lines
    for line in result.stdout.splitlines():
        if line == '\\ No newline at end of file':
            continue
        if file_started_FL:
            if not line.startswith('+'):
                print(f"Unexpected line format after file start: {repr(line)}")
                continue
            lines.append(line[1:])
        else:
            if line.startswith('@@ -0,0 '):
                file_started_FL = True
    return lines


def find_index(ALL_LINES, L, current_rev=None):
    i = 0
    while L:
        if i == len(ALL_LINES):
            return i
        if ALL_LINES[i].endrev is None:
            if ALL_LINES[i].begrev == current_rev:
                pass
            else:
                L -= 1
        elif ALL_LINES[i].endrev == current_rev:
            L -= 1
        i += 1
    while i < len(ALL_LINES) and ALL_LINES[i].endrev is not None:
        i += 1
    return i


def find_next_alive(ALL_LINES, i):
    while True:
        if ALL_LINES[i].endrev is None:
            return i
        i += 1


def print_so_far(fn, ALL_LINES, revs):
    connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    try:
        conn = pyodbc.connect(connectionString)
    except Exception as ex:
        print(f"Failed connection to database {DATABASE}: {str(ex)}")
        return
    cursor = conn.cursor()
    select_table_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{TABLE}'"
    cursor.execute(select_table_query)
    result = cursor.fetchone()
    if result[0] > 0:
        #print(f"The table '{TABLE}' exists in the database.")
        ""
    else:
        print(f"The table '{TABLE}' does not exist in the database.")
        create_table_query = f'''
        CREATE TABLE {TABLE} (
            Code_ID INT PRIMARY KEY,
            File_ID INT,
            File_Name VARCHAR(MAX) NOT NULL,
            Author_Start VARCHAR(MAX),
            Date_Start DATE NOT NULL,
            Author_End VARCHAR(MAX),
            Date_End VARCHAR(MAX),
            Longevity VARCHAR(MAX),
            Comment_Boolean INT NOT NULL,
            Words_Count INT NOT NULL,
            Code VARCHAR(MAX) NOT NULL,
            FOREIGN KEY (File_ID) REFERENCES {TABLE_FOREIGN}(File_ID)
        )
        '''
        print(f"{TABLE} table created successfully")
        cursor.execute(create_table_query)
    head_rev = struct()
    head_rev.hash = ' ' * 8
    head_rev.date = ' ' * 10
    head_rev.author = ' ' * 8
    MAX_LINE_LENGTH = 255 
    for i, line in enumerate(ALL_LINES):
        beg = revs[line.begrev]
        end = revs[line.endrev] if line.endrev is not None else head_rev
        # Discard empty and long lines
        if line.text.strip() and len(line.text) <= MAX_LINE_LENGTH:
            try:
                cursor.execute(f"SELECT MAX(Code_ID) FROM {TABLE}")
                last_id = cursor.fetchone()[0]
                last_id = 0 if last_id is None else last_id + 1
            except Exception as e:
                print("ID error:", e)
                return
            cursor.execute(f"SELECT MAX(File_ID) FROM {TABLE_FOREIGN}")
            file_id = cursor.fetchone()[0]
            file_id = 0 if file_id is None else file_id
            comment_boolean = 1 if line.text.strip().startswith(('#', '//')) else 0
            words_count = len(line.text.split())
            if line.endrev is not None:
                beg_datetime = datetime.strptime(beg.date, '%Y-%m-%d')
                end_datetime = datetime.strptime(end.date, '%Y-%m-%d')
                longevity = (end_datetime - beg_datetime).days
                data_to_insert = (last_id, file_id, fn, beg.author, beg.date, end.author, end.date, longevity, comment_boolean, words_count, line.text)
            else:
                data_to_insert = (last_id, file_id, fn, beg.author, beg.date, 'NULL', 'NULL', 'NULL', comment_boolean, words_count, line.text)
            insert_query = f"INSERT INTO {TABLE} (Code_ID, File_ID, File_Name, Author_Start, Date_Start, Author_End, Date_End, Longevity, Comment_Boolean, Words_Count, Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_query, data_to_insert)
            conn.commit()
    cursor.close()
    conn.close()


def main(fn):
    Quiet = False
    cmd = ['git', 'rev-list', 'HEAD', '--', fn]
    pipe = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
    hashes = pipe.stdout.splitlines()
    if pipe.returncode != 0:
        print(f"Command errored: {' '.join(cmd)}")
        return
    if not Quiet:
        sys.stderr.write('%d revisions\n' % len(hashes))
    cmd = ['git', 'log', '--format=%ad %cn', '--date=short', fn]
    pipe = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
    date_author = pipe.stdout.splitlines()
    if pipe.returncode != 0:
        print(f"Command errored: {' '.join(cmd)}")
        return
    assert len(hashes) == len(date_author), ('mismatch between output of "git rev-list" and "git log"', hashes, date_author)
    revs = []
    for hash, date_au in zip(hashes, date_author):
        x = struct()
        x.hash = hash.strip()
        x.date, x.author = date_au.split(' ', 1)
        x.author = x.author.strip()
        revs.append(x)
    if not Quiet:
        sys.stderr.write('%s --- %s\n' % (revs[-1].date, revs[0].date))
    forced_author_len = 100
    for x in revs:
        if len(x.author) > forced_author_len:
            x.author = x.author[:forced_author_len - 1] + '.'
        else:
            x.author = x.author.ljust(forced_author_len)
    ALL_LINES = []
    for line in get_initial_version(revs[-1].hash, fn):
        x = struct()
        x.text = line
        x.begrev = len(revs) - 1
        x.endrev = None
        ALL_LINES.append(x)
    # Initial version
    print_so_far(fn, ALL_LINES, revs)
    origL, del_N, newL, add_N = 0, 0, 0, 0
    for r in range(len(revs) - 1, 0, -1):
        if not Quiet:
            sys.stderr.write('\r')
            sys.stderr.write('Processing revision: (%d/%d) %s' % (len(revs) - r + 1, len(revs), revs[r - 1].date))
        cmd = ['git', 'diff', '-U0', revs[r].hash, revs[r - 1].hash, fn]
        pipe = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
        if pipe.returncode != 0:
            print(f"Command errored: {' '.join(cmd)}")
            continue
        in_header_FL = True
        for line in pipe.stdout.splitlines():
            if in_header_FL:
                if line.startswith('@@'):
                    in_header_FL = False
                else:
                    continue
            if line == '\\ No newline at end of file':
                continue
            if line.startswith('@@'):
                origL, del_N, newL, add_N = parse_chunk_header(line)
                all_index = None
            elif del_N:
                assert line.startswith('-'), line
                if all_index is None:
                    all_index = find_index(ALL_LINES, origL - 1, current_rev=r - 1)
                else:
                    all_index = find_next_alive(ALL_LINES, all_index)
                assert ALL_LINES[all_index].text == line[1:], ("diff processing screwed up, marking the wrong deletion line", ALL_LINES[all_index].text, line, all_index)
                ALL_LINES[all_index].endrev = r - 1
                del_N -= 1
                if del_N == 0:
                    all_index = None
            elif add_N:
                assert line.startswith('+'), line
                if all_index is None:
                    all_index = find_index(ALL_LINES, newL - 1)
                else:
                    all_index += 1
                x = struct()
                x.text = line[1:]
                x.begrev = r - 1
                x.endrev = None
                ALL_LINES.insert(all_index, x)
                add_N -= 1
                if add_N == 0:
                    all_index = None
            else:
                if line.startswith('diff'):
                    in_header_FL = True
                else:
                    assert 0, ("shouldn't reach here unless misparsed diff output", line)
        # Modified lines
        print()
        print_so_far(fn, ALL_LINES, revs)
    if not Quiet:
        sys.stderr.write('\n')
    # Alive lines
    print_so_far(fn, ALL_LINES, revs)


if __name__ == '__main__':
    main()