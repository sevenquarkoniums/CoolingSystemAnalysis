#!/bin/bash

for i in `hostname`;
                   do
                       nodename=$i
                   done
echo $nodename
echo $OMP_NUM_THREADS
echo $KMP_AFFINITY
dat_home=$1
tracepath=$2
pkglim=$3
corefreq=$4
thread_count=$5
#echo $thread_count
#echo $affinity

traceprefix="rank"
nnodes=1
nranks=1
nranks_per_socket=1
apptracename=cg.C
appname=cg.C
appdir=${dat_home}/benchmarks/NPB-MZ/bin
inputdata=""

cd ${appdir}

samplingint=200

curr_trace=${tracepath}/${nodename}/
#curr_trace=/g/g92/marathe1/quartz/model/trace2
#curr_trace=/tmp/marathe1/traces
mkdir -p ${curr_trace}
echo "Execution begins @ ", $(date +%s) > ${curr_trace}/local_time_stamp_log
chmod 777 ${curr_trace} -R
#KMP_AFFINITY=compact,verbose PROCESS_PER_SAMPLER=${nranks} \
#SINGLE_INSTANCE=1 \
#OMP_NUM_THREADS=${thread_count} KMP_AFFINITY=${affinity} \
MV2_ENABLE_AFFINITY=0 \
MV2_USE_AFFINITY=0 \
PKG_POWERLIMIT=${pkglim} DRAM_POWERLIMIT=-1.0 \
PROCESS_PER_SAMPLER=${nranks} \
ENABLE_SAMPLING=1 SAMPLING_INTERVAL=${samplingint} \
OMP_NUM_THREADS=${thread_count} \
ENABLE_OPENMP_DATA=0 \
SINGLE_INSTANCE=1 \
ENABLE_MPI_DATA=0 \
ENABLE_PHASE_FILE=0 \
ENABLE_MSR_DATA=1 \
ENABLE_POWER_DATA=1 \
TRACEFILE_PATH=${curr_trace} \
TRACE_PREFIX="rank" \
${appdir}/${appname} ${inputdata} 2>&1 >& /tmp/out.log


#srun -N ${nnodes} -n ${nranks} \
#mpirun -np ${nranks} \
#/usr/tce/packages/impi/impi-2017.1-intel-17.0.0/bin/mpirun -np ${nranks} \
mv ${curr_trace}/rank_* ${curr_trace}/rank_0
mv /tmp/out.log ${curr_trace}/
#cp ${curr_trace}/rank_0 ${tracepath}/
#/bin/rm ${curr_trace}/rank_0 -f

cd -
echo "Execution ends @ ", $(date +%s) >> ${curr_trace}/local_time_stamp_log
