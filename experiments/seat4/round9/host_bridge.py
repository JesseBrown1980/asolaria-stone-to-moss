#!/usr/bin/env python3
"""Seat4 R9 bridge: real process CPU and memory counters; NO power or photon sensor."""
import hashlib,json,os,platform,sys,time,tracemalloc
from pathlib import Path

BANK_SHA="52b4e6b9fc10f641e677c87382b137ec21a15e322ef19c20eb03735254b36345"
SRC_SHA="02ff42a93d934074ae9c83e1b989f097944c8c7cd2ed80197c2cfd8795391e22"
N=4096;MIB=1024*1024
def digest(b):return hashlib.sha256(b).hexdigest()
def wire(d):return (json.dumps(d,sort_keys=True,separators=(",",":"),ensure_ascii=True)+"\n").encode("ascii")
def require(c,m):
 if not c:raise ValueError(m)
def maximum_resident():
 if os.name=="nt":
  try:
   import ctypes
   from ctypes import wintypes
   class Counters(ctypes.Structure):
    _fields_=[("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD),
      ("PeakWorkingSetSize",ctypes.c_size_t),("WorkingSetSize",ctypes.c_size_t),
      ("QuotaPeakPagedPoolUsage",ctypes.c_size_t),("QuotaPagedPoolUsage",ctypes.c_size_t),
      ("QuotaPeakNonPagedPoolUsage",ctypes.c_size_t),("QuotaNonPagedPoolUsage",ctypes.c_size_t),
      ("PagefileUsage",ctypes.c_size_t),("PeakPagefileUsage",ctypes.c_size_t)]
   c=Counters();c.cb=ctypes.sizeof(Counters)
   kernel=ctypes.WinDLL("kernel32",use_last_error=True)
   kernel.GetCurrentProcess.restype=wintypes.HANDLE
   handle=kernel.GetCurrentProcess()
   fn=ctypes.WinDLL("psapi",use_last_error=True).GetProcessMemoryInfo
   fn.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
   fn.restype=wintypes.BOOL
   if fn(handle,ctypes.byref(c),ctypes.sizeof(c)):return int(c.PeakWorkingSetSize),"Windows PSAPI PeakWorkingSetSize (bytes)"
  except Exception:return None,"Windows process RSS unavailable"
  return None,"Windows PSAPI call failed"
 try:
  import resource
  used=resource.getrusage(resource.RUSAGE_SELF)
  # Linux ru_maxrss is in KiB; on macOS bytes.
  if sys.platform.startswith("linux"):return int(used.ru_maxrss)*1024,"Linux getrusage ru_maxrss (KiB, converted)"
  if sys.platform=="darwin":return int(used.ru_maxrss),"Darwin getrusage ru_maxrss bytes"
  return None,"Other resource ru_maxrss units not independently resolved"
 except Exception:return None,"resource module unavailable"

def run(inputroot,output):
 output.mkdir(parents=True,exist_ok=True)
 bank=(inputroot/"rainbow-evidence/rainbow7-bank.jsonl").read_bytes()
 source=(inputroot/"base-evidence/lightbank-memories.json").read_bytes()
 require(len(bank)==184815 and digest(bank)==BANK_SHA,"REAL_ARCHIVED_BANK_INPUT_CHANGED")
 require(len(source)==16689 and digest(source)==SRC_SHA,"REAL_ARCHIVED_SOURCE_INPUT_CHANGED")
 wrong=bytearray(bank);wrong[0]^=1
 require(digest(wrong)!=BANK_SHA,"BANK_BIT_FAULT_FAILED_TO_DETECT")
 del wrong

 tracemalloc.start()
 start_real=time.time_ns()
 start_wall=time.perf_counter_ns()
 start_cpu=time.process_time_ns()
 # Actually allocate and touch 4MiB of addressable process-private memory.
 scratch=bytearray(4*MIB)
 for i in range(0,len(scratch),4096):scratch[i]=(i//4096)&255
 touched=sum(scratch[::4096])
 h=hashlib.sha256()
 for k in range(N):h.update(bank)
 work_sha=h.hexdigest()
 cpu_ns=time.process_time_ns()-start_cpu
 wall_ns=time.perf_counter_ns()-start_wall
 end_real=time.time_ns()
 _,alloc_peak=tracemalloc.get_traced_memory()
 rss,method=maximum_resident()
 tracemalloc.stop()
 del scratch
 require(cpu_ns>0 and wall_ns>0 and alloc_peak>=4*MIB,"HOST_PROCESS_METRIC_NOT_RECORDED")
 require(0<=touched<262144,"MEMORY_TOUCH_INCONSISTENT")
 # Deterministic scientific content: SHOULD be byte identical across distinct hosts.
 core={"schema":"ASOLARIA-SEAT4-R9-SOURCE-HOST-EVIDENCE-V1",
 "source_records_sha256":SRC_SHA,"source_bank_sha256":BANK_SHA,
 "source_bank_bytes":len(bank),"hash_iterations":N,
 "original_bank_bytes_processed":len(bank)*N,
 "workload_sha256":work_sha,
 "source_tamper_test":"REJECTED_BY_PINNED_SHA256",
 "physical_hardware_execution":"OS_PROCESS_METRICS_PRESENT",
 "actual_electrical_energy_instrumented":False,
 "actual_optical_detector_instrumented":False,
 "actual_neural_electrophysiology_instrumented":False}
 # Per-host data are deliberately NOT byte-identical; no fabricated shared timings.
 measurements={
 "schema":"ASOLARIA-SEAT4-R9-HOST-COUNTERS-V1",
 "source_bank_sha256":BANK_SHA,"workload_sha256":work_sha,
 "environment_os":platform.system(),"environment_os_release":platform.release(),
 "python_version":platform.python_version(),
 "git_run_id":os.getenv("GITHUB_RUN_ID"),
 "git_run_attempt":os.getenv("GITHUB_RUN_ATTEMPT"),
 "git_sha":os.getenv("GITHUB_SHA"),
 "runner_name_provider_claim":os.getenv("RUNNER_NAME"),
 "runner_os_provider_claim":os.getenv("RUNNER_OS"),
 "process_pid":os.getpid(),
 "wall_start_time_unix_ns_OS":start_real,"wall_end_time_unix_ns_OS":end_real,
 "host_process_cpu_time_ns_OS":cpu_ns,
 "monotonic_elapsed_ns_OS":wall_ns,
 "tracemalloc_peak_python_allocation_bytes":alloc_peak,
 "observed_process_peak_resident_bytes":rss,
 "resident_meter_source":method,
 "scratch_allocation_bytes":4*MIB,
 "scratch_bytes_physically_written_by_process":1024,
 "measured_ac_wall_energy_joules":None,
 "measured_dc_rail_voltage_volts":None,
 "measured_dc_current_amperes":None,
 "measured_optical_photon_counts":None,
 "measured_acoustic_phonon_counts":None,
 "spectrometer_raw_sha256":None,
 "provider_self_report_is_independent_electrical_attestation":False}
 for name,obj in [("r9-science.json",core),("r9-host.json",measurements)]:
  b=wire(obj);(output/name).write_bytes(b)
  (output/(name+".sha256")).write_bytes((digest(b)+"  "+name+"\n").encode("ascii"))
 print(json.dumps({"verdict":"REAL_OS_COUNTERS_AND_DIGITAL_SHA_RECORDED","bank_sha256":BANK_SHA,
 "workload_sha256":work_sha,"host_cpu_ns":cpu_ns,"host_elapsed_ns":wall_ns,
 "peak_alloc_bytes":alloc_peak,"peak_rss_bytes":rss,
 "direct_meter_energy_photons":None},sort_keys=True))
if __name__=="__main__":
 if len(sys.argv)!=3:raise SystemExit("usage: python host_bridge.py ORIGINAL_PR80_ARCHIVE OUT")
 run(Path(sys.argv[1]),Path(sys.argv[2]))
