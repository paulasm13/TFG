"""

ARCHIVO PARA ANALIZAR UN FICHERO 

"""


import sys
import os
import re
import pyodbc
from datetime import datetime


SERVER = 'LAPTOP-E26LIVT1\SQLEXPRESS'
DATABASE = 'Analysis_Github_Repository'
TABLE = 'Code'


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


def get_initial_version(first_rev,fn):
  lines = []
  file_started_FL = False
  for line in os.popen('git show %s %s'%(first_rev,fn)):
    if line=='\ No newline at end of file\n':
        continue
    if file_started_FL:
      assert line[0]=='+',("don't recognize format",line)
      lines.append(line[1:]) # take out the leading '+'
    else:
      if line.startswith('@@ -0,0 '):
        file_started_FL=True
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
        ID INT PRIMARY KEY,
        File_Name VARCHAR(50) NOT NULL,
        Author_beg VARCHAR(50),
        Date_beg DATE NOT NULL,
        Author_end VARCHAR(50),
        Date_end VARCHAR(50),
        Longevity INT,
        Code VARCHAR(MAX) NOT NULL,
    )
    '''
    cursor.execute(create_table_query)

  head_rev = struct()
  head_rev.hash = '        '
  head_rev.date = '          '
  head_rev.author = '        '
  i=0
  for line in ALL_LINES:
    code = line.text
    beg = revs[line.begrev]
    end = revs[line.endrev] if line.endrev is not None else head_rev
    
    # Blank lines or comments
    if not (code.strip().startswith('#') or len(code.strip()) == 0 or code.strip().startswith('//')):
      # ID PRIMARY KEY
      try:
        cursor.execute(f"SELECT MAX(ID) FROM {TABLE}")
        last_id = cursor.fetchone()[0]

        if last_id is None:
          last_id = 0

        id = last_id + 1

      except Exception as e:
          print("Error al incrementar el ID:", e)
          return None

      # Deleted lines
      if line.endrev is not None:
        print('-%s (%s %s) +%s (%s %s)'%(end.hash[:8],end.author,end.date,beg.hash[:8],beg.author,beg.date),line.text, end=' ')
        beg_datetime = datetime.strptime(beg.date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end.date, '%Y-%m-%d')
        long = end_datetime - beg_datetime
      
        insert_query = f"INSERT INTO {TABLE} (File_Name, Author_end, Author_beg, Date_beg, Date_end, Code, ID, Longevity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        data_to_insert = (fn, end.author, beg.author, beg.date, str(end.date), line.text, id, int(long.days))
        cursor.execute(insert_query, data_to_insert)
        conn.commit() 
        
      # Current lines
      else:
        print(' %s  %s %s  +%s (%s %s)'%(end.hash[:8],end.author,end.date,beg.hash[:8],beg.author,beg.date),line.text, end=' ')
        current_datetime = datetime.now()
        beg_datetime = datetime.strptime(beg.date, '%Y-%m-%d')
        long = current_datetime - beg_datetime
      
        insert_query = f"INSERT INTO {TABLE} (File_Name, Author_end, Author_beg, Date_beg, Date_end, Code, ID, Longevity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        data_to_insert = (fn, 'NULL', beg.author, beg.date, 'NULL', line.text, id, int(long.days))
        cursor.execute(insert_query, data_to_insert)
        conn.commit()
    else:
      pass 

  cursor.close()
  conn.close()


def main(fn):
  Quiet = False

  # GET ALL REVISIONS
  cmd = 'git rev-list HEAD -- %s' % fn
  print('[cmd]',cmd)
  pipe        = os.popen(cmd)
  hashes      = pipe.readlines()

  assert not pipe.close(), ('Command errored',cmd)
        
  if not Quiet:
    sys.stderr.write('%d revisions\n'%(len(hashes)))

        
  # GET REVISION INFO
  cmd         = 'git log --format="%%ad %%cn" --date=short %s'%fn
  print('[cmd]',cmd)
  pipe        = os.popen(cmd)
  date_author = pipe.readlines()

  assert not pipe.close(), ('Command errored',cmd)

  assert len(hashes)==len(date_author), ('mismatch between output of "git rev-list" and "git log"', hashes, date_author)
      
  revs = []
  for hash, date_au in zip(hashes,date_author):
    x = struct()
    x.hash = hash.strip()
    x.date, x.author = date_au.split(' ',1)
    x.author = x.author.strip()
    revs.append(x)
      
  if not Quiet:
    sys.stderr.write('%s --- %s\n'%(revs[-1].date,revs[0].date))
        
  forced_author_len = 8
  for x in revs:
    if len(x.author) > forced_author_len:
      x.author = x.author[:forced_author_len-1]+'.'
    else:
      x.author = x.author.ljust(forced_author_len)
      
  # INITIAL VERSION
  ALL_LINES=[]                        
  for line in get_initial_version(revs[-1].hash,fn):
    x = struct()
    x.text    = line
    x.begrev  = len(revs)-1
    x.endrev  = None
    ALL_LINES.append(x)  
      
  print_so_far(fn, ALL_LINES,revs)

      
  # process all the revisions
  origL, del_N, newL, add_N = 0,0,0,0
  for r in range(len(revs)-1,0,-1):
      
    if not Quiet:
      sys.stderr.write('\r')
      sys.stderr.write('Processing revision: (%d/%d) %s' % (len(revs)-r+1,len(revs),revs[r-1].date))
        
    cmd  = 'git diff -U0 %s %s %s'%(revs[r].hash,revs[r-1].hash,fn)
    pipe = os.popen(cmd)
        
    print('[cmd]',cmd)
    print()

    in_header_FL = True
    for line in pipe:

        if in_header_FL:              # SKIP OVER HEADER
            if line.startswith('@@'): # we hit our first chunk
                in_header_FL = False
            else:
                continue
                
        if line=='\ No newline at end of file\n':
            continue
                
        print('[line]',repr(line),'add_N=%d del_N=%d'%(add_N,del_N))
            
        if line.startswith('@@'):     # RECEIVED A NEW CHUNK!
          origL, del_N, newL, add_N = parse_chunk_header(line)
          all_index = None
          print('chunk',origL,del_N,newL,add_N)
              
        elif del_N:                   # PROCESSING DELETED LINES
          assert line.startswith('-'),line
          if all_index is None:       # find index in ALL_LINES for origL
            all_index = find_index(ALL_LINES, origL-1, current_rev=r-1)
          else:
            all_index = find_next_alive(ALL_LINES, all_index)
              
          assert ALL_LINES[all_index].text == line[1:], (
            "diff processing screwed up, marking the wrong deletion line",ALL_LINES[all_index].text,line,all_index)
          ALL_LINES[all_index].endrev = r-1
              
          del_N -= 1
          if del_N == 0:
            all_index = None
              
        elif add_N:                   # PROCESSING ADDED LINES
          assert line.startswith('+'),line
          if all_index is None:
            all_index = find_index(ALL_LINES, newL-1)
          else:
            all_index += 1
                          
          x = struct()
          x.text = line[1:]
          x.begrev = r-1
          x.endrev = None
              
          ALL_LINES.insert(all_index, x)
              
          add_N -= 1
          if add_N == 0:
            all_index = None
              
        else:
          if line.startswith('diff'):
            in_header_FL = True
          else:
            assert 0, ("shouldn't reach here unless misparsed diff output",line)
            
    assert not pipe.close(), ('Command errored',cmd)
        
    print()
    print_so_far(fn, ALL_LINES,revs)
      
  if not Quiet:
    sys.stderr.write('\n')
  print_so_far(fn, ALL_LINES,revs)


