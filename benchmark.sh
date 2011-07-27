#!/bin/bash

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 [options] file [file2...]"
  echo "  -1 --py    benchmark py-css"
  echo "  -2 --ncss  benchmark ncss"
  echo "  -y --yui   benchmark YUICompressor"
  echo
  echo "  If no benchmark options are given, all compressor will"
  echo "  be benchmarked."
  exit 1
fi

declare -i K=2

rpad()
{
  word="$1"
  while [ ${#word} -lt $2 ]; do
    word="$word$3"
  done
  echo -n "$word"
}

lpad()
{
  word="$1"
  while [ ${#word} -lt $2 ]; do
    word="$3$word"
  done
  echo -n "$word"
}

run()
{
  declare -i m
  declare -i s
  declare -i n
  declare -i avg
  declare -a times
  declare -i runs
  declare t

  times=()
  avg=-1
  runs=0
  while [ $avg -eq -1 ]; do
    ((runs += 1))
    t=`{ time $2 <$1 >/dev/null; } 2>&1`
    read m s ms < <(echo $t | sed 's/real \([0-9]*\)m\([0-9]*\).\([0-9]*\)s user .*/\1 \2 \3/')
    # sometimes ms comes in as '008', need to deal with that
    if [[ ${ms:0:2} == "00" ]]; then
      ms=${ms:2}
    elif [[ ${ms:0:1} == "0" ]]; then
      ms=${ms:1}
    fi
    n=$ms
    if [[ $s -gt 0 ]]; then
      ((n += $s * 1000))
    fi
    if [[ $m -gt 0 ]]; then
      ((n += $m * 60000))
    fi
    ((n /= 10))
    if [[ "${times[$n]}" == "" ]]; then
      times[$n]=1
    elif [ ${times[$n]} -eq $K ]; then
      avg=$n
      ((avg *= 10))
    else
      ((times[$n] += 1))
    fi
  done

  echo "$avg"
}

files=()
benches=()
commands=()

addPy()
{
  benches+=('py-css')
  commands+=('./runner.py')
}

addN()
{
  benches+=('ncss')
  commands+=('ncss')
}

addY()
{
  benches+=('yui-2.4.2' 'yui-2.4.6')
  commands+=("java -jar yuicompressor-2.4.2.jar --type css" "java -jar yuicompressor-2.4.6.jar --type css")
}

for i in $*
do
  case $i in
    -1|--py)
      addPy
      ;;
    -2|--ncss)
      addN
      ;;
    -y|--yui)
      addY
      ;;
    *)
      files+=("$i")
      ;;
  esac
done

if [[ ${#benches} -eq 0 ]]; then
  addPy
  addN
  addY
fi

echo -n "file                   size  lines"
for b in ${benches[@]}; do
  echo -n "  $b"
done
echo

# run benchmarks for each input file
for file in ${files[@]}; do
  rpad $file 18 ' '

  # size
  echo -n '  '
  size=`ls -l $file | cut -c 28-35`
  lpad $size 7 ' '

  # lines
  echo -n '  '
  L=`wc -l $file | cut -c 1-8`
  lpad $L 5 ' '

  count=${#commands[@]}
  for ((i=0; i < $count; i++)); do
    echo -n '  '
    ms=`run $file "${commands[$i]}"`
    lpad $ms ${#benches[$i]} ' '
  done

  echo
done
