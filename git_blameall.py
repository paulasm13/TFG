"""

ARCHIVO PARA ANALIZAR UN FICHERO 

"""


import sys
import subprocess
import re
import pyodbc
from datetime import datetime


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE = 'Code'
TABLE_FOREIGN = 'Files'


class struct:
  pass


def parse_chunk_header(s):
  Chunk_Header_Pat = re.compile('@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@') 
  origL, del_N, newL, add_N = Chunk_Header_Pat.match(s).groups()
  if del_N is None:
    del_N = 1
  if add_N is None:
    add_N = 1
    
  return list(map(int,(origL, del_N, newL, add_N)))


def get_initial_version(first_rev, fn):
  lines = []
  file_started_FL = False
  cmd = ['git', 'show', '%s' % first_rev, fn]
  try:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
    result.check_returncode()  # Raise CalledProcessError if the command returned an error
  except subprocess.CalledProcessError as e:
    print(f"Error executing command: {e}")
    return lines
  for line in result.stdout.splitlines():
    if line == '\ No newline at end of file':
      continue
    if file_started_FL:
      if not line.startswith('+'):
        print(f"Unexpected line format after file start: {repr(line)}")
        continue
      lines.append(line[1:]) # take out the leading '+'
    else:
        if line.startswith('@@ -0,0 '):
          file_started_FL = True
  return lines


def find_index(ALL_LINES,L,current_rev=None):
  i=0
  while L:
    if i==len(ALL_LINES):               # appending to the end
      return i
    if ALL_LINES[i].endrev == None: # this line is still alive
      if ALL_LINES[i].begrev==current_rev: # this line was inserted during the current revision, doesn't count
        pass
      else:
        L-=1 # count the line
    elif ALL_LINES[i].endrev == current_rev: # still count the line, it was erased during the current revision
      L-=1
    i+=1
  # ffwd through deleted lines
  while i<len(ALL_LINES) and ALL_LINES[i].endrev!=None:
    i+=1
  return i


def find_next_alive(ALL_LINES,i):
  while 1:
    if ALL_LINES[i].endrev==None:
      return i
    i+=1


def print_so_far(fn, ALL_LINES,revs): 
  # BBDD connection
  connectionString = f'DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

  try:
    conn = pyodbc.connect(connectionString)
    print(f"Successful connection to database {DATABASE}")
  except Exception as ex:
    print(f"Failed connection to database {DATABASE}: {str(ex)}")

  cursor = conn.cursor()

  # CREATE TABLE OR NOT
  select_table_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{TABLE}'"
  cursor.execute(select_table_query)
  result = cursor.fetchone()

  if result[0] > 0:
    print(f"The table '{TABLE}' exists in the database.")
  else:
    print(f"The table '{TABLE}' does not exist in the database.")
    create_table_query = f'''
    CREATE TABLE {TABLE} (
        Code_ID INT PRIMARY KEY,
        File_ID INT,
        File_Name VARCHAR(50) NOT NULL,
        Author_Start VARCHAR(50),
        Date_Start DATE NOT NULL,
        Author_End VARCHAR(50),
        Date_End VARCHAR(50),
        Longevity VARCHAR(50),
        Comment_Boolean INT NOT NULL,
        Words_Count INT NOT NULL,
        Code VARCHAR(MAX) NOT NULL,
        FOREIGN KEY (File_ID) REFERENCES {TABLE_FOREIGN}(File_ID),
    )
    '''
    cursor.execute(create_table_query)

  head_rev = struct()
  head_rev.hash = '        '
  head_rev.date = '          '
  head_rev.author = '        '
  i=0
  for line in ALL_LINES:
    beg = revs[line.begrev]
    end = revs[line.endrev] if line.endrev is not None else head_rev
    
    # If not blank lines...
    if not (len(line.text.strip()) == 0):
      # ID PRIMARY KEY
      try:
        cursor.execute(f"SELECT MAX(Code_ID) FROM {TABLE}")
        last_id = cursor.fetchone()[0]

        if last_id is None:
          last_id = 0

        id = last_id + 1

      except Exception as e:
          print("ID error:", e)
          return None
      
      # ID FOREIGN KEY
      cursor.execute(f"SELECT MAX(File_ID) FROM {TABLE_FOREIGN}")
      file_id = cursor.fetchone()[0]

      if file_id is None:
          file_id = 0
      
      # Comments
      if (line.text.strip().startswith('#') or line.text.strip().startswith('//')):
        comment_boolean = 1
      else:
        comment_boolean = 0

      # Words count
      words_count = len(line.text.split())

      # Deleted lines
      if line.endrev is not None:
        #print('-%s (%s %s) +%s (%s %s)'%(end.hash[:8],end.author,end.date,beg.hash[:8],beg.author,beg.date),line.text, end=' ')
        beg_datetime = datetime.strptime(beg.date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end.date, '%Y-%m-%d')
        long = end_datetime - beg_datetime
      
        insert_query = f"INSERT INTO {TABLE} (Code_ID, File_ID, File_Name, Author_Start, Date_Start, Author_End, Date_End, Longevity, Comment_Boolean, Words_Count, Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data_to_insert = (id, file_id, fn, beg.author, beg.date, end.author, str(end.date), long.days, comment_boolean, words_count, line.text)
        cursor.execute(insert_query, data_to_insert)
        conn.commit() 
        
      # Current lines
      else:
        #print(' %s  %s %s  +%s (%s %s)'%(end.hash[:8],end.author,end.date,beg.hash[:8],beg.author,beg.date),line.text, end=' ')
        insert_query = f"INSERT INTO {TABLE} (Code_ID, File_ID, File_Name, Author_Start, Date_Start, Author_End, Date_End, Longevity, Comment_Boolean, Words_Count, Code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        data_to_insert = (id, file_id, fn, beg.author, beg.date, 'NULL', 'NULL', 'NULL', comment_boolean, words_count, line.text)
        cursor.execute(insert_query, data_to_insert)
        conn.commit()
    else:
      pass 

  cursor.close()
  conn.close()


def main(fn):
    Quiet = False

    # GET ALL REVISIONS
    cmd = ['git', 'rev-list', 'HEAD', '--', fn]
    pipe = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='ignore')
    hashes = pipe.stdout.splitlines()
    if pipe.returncode != 0:
      print(f"Command errored: {' '.join(cmd)}")
      return

    if not Quiet:
        sys.stderr.write('%d revisions\n' % len(hashes))

    # GET REVISION INFO
    cmd = ['git', 'log', '--format=%ad %cn', '--date=short', fn]
    #print('[cmd]', ' '.join(cmd))
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

    forced_author_len = 8
    for x in revs:
        if len(x.author) > forced_author_len:
            x.author = x.author[:forced_author_len - 1] + '.'
        else:
            x.author = x.author.ljust(forced_author_len)

    # INITIAL VERSION
    ALL_LINES = []
    for line in get_initial_version(revs[-1].hash, fn):
        x = struct()
        x.text = line
        x.begrev = len(revs) - 1
        x.endrev = None
        ALL_LINES.append(x)

    print_so_far(fn, ALL_LINES, revs)

    # process all the revisions
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

        print('[cmd]', ' '.join(cmd))
        print()

        in_header_FL = True
        for line in pipe.stdout.splitlines():
          if in_header_FL:  # SKIP OVER HEADER
              if line.startswith('@@'):  # we hit our first chunk
                  in_header_FL = False
              else:
                  continue

          if line == '\ No newline at end of file':
              continue

          #print('[line]', repr(line), 'add_N=%d del_N=%d' % (add_N, del_N))

          if line.startswith('@@'):  # RECEIVED A NEW CHUNK!
              origL, del_N, newL, add_N = parse_chunk_header(line)
              all_index = None
              #print('chunk', origL, del_N, newL, add_N)

          elif del_N:  # PROCESSING DELETED LINES
              assert line.startswith('-'), line
              if all_index is None:  # find index in ALL_LINES for origL
                  all_index = find_index(ALL_LINES, origL - 1, current_rev=r - 1)
              else:
                  all_index = find_next_alive(ALL_LINES, all_index)

              print("Expected line:", repr(line[1:]))
              print("Actual line:", repr(ALL_LINES[all_index].text))

              assert ALL_LINES[all_index].text == line[1:], (
                "diff processing screwed up, marking the wrong deletion line", ALL_LINES[all_index].text, line,
                all_index)
              ALL_LINES[all_index].endrev = r - 1

              del_N -= 1
              if del_N == 0:
                  all_index = None

          elif add_N:  # PROCESSING ADDED LINES
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

        print()
        print_so_far(fn, ALL_LINES, revs)

    if not Quiet:
        sys.stderr.write('\n')
    print_so_far(fn, ALL_LINES, revs)

if __name__=='__main__':
  main()
