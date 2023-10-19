from sys import argv
from impatto import main


if __name__ == "__main__":
  benchmark_name = argv[1]
  others = argv[2:]

  if "range" in others:
    print("Did you mean to use max-range instead of range? [ /n]:")
    answer = input()
    if answer == "y" or answer == "Y" or answer == "" or answer == " ":
      others[others.index("range")] = "max-range"

  program_dir, input_dir, bucket_dir = "examples", "inputs", "buckets"

  program_file = f"{program_dir}/{benchmark_name}.spl"
  input_file = f"{input_dir}/{benchmark_name}.json"
  bucket_file = f"{bucket_dir}/{benchmark_name}.json"
  
  match benchmark_name:
    case "popl-full":
      program_file = f"{program_dir}/popl.spl"
      input_file = f"{input_dir}/popl-full.json"
      bucket_file = f"{bucket_dir}/popl.json"
    case "popl-a":
      program_file = f"{program_dir}/popl.spl"
      input_file = f"{input_dir}/popl-a.json"
      bucket_file = f"{bucket_dir}/popl.json"
    case "popl-b":
      program_file = f"{program_dir}/popl.spl"
      input_file = f"{input_dir}/popl-b.json"
      bucket_file = f"{bucket_dir}/popl.json"
    case "excel-transposition":
      program_file = f"{program_dir}/excel.spl"
      input_file = f"{input_dir}/excel-transposition.json"
      bucket_file = f"{bucket_dir}/excel.json"
    case "excel-boolean":
      program_file = f"{program_dir}/excel.spl"
      input_file = f"{input_dir}/excel-transposition.json"
      bucket_file = f"{bucket_dir}/excel-boolean.json"
    case "excel-relaxed":
      program_file = f"{program_dir}/excel.spl"
      input_file = f"{input_dir}/excel.json"
      bucket_file = f"{bucket_dir}/excel-relaxed.json"
    case "cate2-bounded":
      program_file = f"{program_dir}/cate2.spl"
      input_file = f"{input_dir}/cate2.json"
      bucket_file = f"{bucket_dir}/cate2-bounded.json"
    case "diabetes":
      program_file = f"networks/python/diabetes__0_1_2_3_4__4_4.py"
      input_file = f"{input_dir}/networks.json"
      bucket_file = f"{bucket_dir}/network2.json"



  if "popl" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("interproc")

  if "excel" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("interproc-fast")

  if "linear" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("interproc-strong")

  if "ex" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("interproc-strong")

  if "rr" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("interproc-fast")

  if "cate" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("interproc-strong")

  if "diabetes" in benchmark_name and "--engine" not in others:
    others.append("--engine")
    others.append("qlibra")

  if "diabetes" in benchmark_name and "--analysis" not in others:
    others.append("--analysis")
    others.append("changes")


  if "cate2" == benchmark_name and ("range" in others or "max-range" in others):
    bucket_file = f"{bucket_dir}/cate2-bounded.json"

  args = [
    program_file,
    input_file,
    bucket_file,
    *others
  ]  

  main(args)
