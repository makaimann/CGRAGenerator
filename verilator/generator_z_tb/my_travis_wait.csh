#!/bin/csh -f

set max = $1
set i = 0

while ($i < $max)
  echo ------------------------------
  echo MY TRAVIS WAIT $i/$max minutes
  sleep 60
  @ i = $i + 1

  ls -lt /tmp | head
  if (-d obj_dir) ls -lt obj_dir | head
  echo ------------------------------
end
