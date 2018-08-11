#!/usr/bin/env python
#coding=utf-8
import requests
import json
import time
import rrdtool
import os
import MySQLdb
conn=MySQLdb.connect(host='localhost',user='root',passwd='sklois123',db='cloudmonitor',port=3306)
cur=conn.cursor()
cur.execute('select * from cloud_threshold')
line=cur.fetchall()[0]
original_path='/var/lib/collectd/rrd/'
start_time='-20s'
end_time='now'
CF='AVERAGE'
resolution='10s'
for filename in os.listdir(original_path):
	if 'instance' not in filename:		
		physical_name=filename
file=os.listdir(original_path)
file.sort()  
def check_pcpu(var,limit):
        if var[2][1][0] is not None:
                value1=100-var[2][1][0]
        elif var[2][0][0] is not None:
                value1=100-var[2][0][0]
        else:
                value1='#'

        if value1 == '#':
                value2="Unkown"
        elif value1 < limit:
                value2="Normal"
        else:
                value2="Warning"
        return (value1,value2)
def check_mem(var):
        if var[2][1][0] is not None:
                value=round(var[2][1][0]/1024/1024,2)
        elif var[2][0][0] is not None:
                value=round(var[2][0][0]/1024/1024,2)
        else:
                value='#'
        return value
def check_single(var):
	if  var[2][1][0] is not None:
                value=var[2][1][0]
	elif var[2][0][0] is not None:
                value=var[2][0][0]
	else:
                value='#'
	return value
def check_tri(var,limit):
	if  var[2][1][0] is not None:
		value1=var[2][1][0]
		value2=var[2][1][1]
		value3=var[2][1][2]
	elif var[2][0][0] is not None:
                value1=var[2][0][0]
                value2=var[2][0][1]
                value3=var[2][0][2]
	else:
		value1='#'
		value2='#'
		value3='#'
	if value2!='#':
		if value2 < limit:
			value4="Normal"
		else:
			value4="Warning"
	else:
		value4="Unkown"
	return (value1,value2,value3,value4)
flow_tcp = {'keys':'ipsource,ipdestination,tcpsourceport,tcpdestinationport,inputifindex,outputifindex,tcpflags','value':'bytes','log':True}
requests.put('http://localhost:8008/flow/flow_tcp/json',data=json.dumps(flow_tcp))

flow_udp = {'keys':'ipsource,ipdestination,udpsourceport,udpdestinationport,inputifindex,outputifindex','value':'bytes','log':True}
requests.put('http://localhost:8008/flow/flow_udp/json',data=json.dumps(flow_udp))

flow_icmp = {'keys':'ipsource,ipdestination,inputifindex,outputifindex,icmptype','value':'bytes','log':True}
requests.put('http://localhost:8008/flow/flow_icmp/json',data=json.dumps(flow_icmp))

flow_http = {'keys':'ipsource,ipdestination,httpmethod,httpurl','value':'bytes','log':True}
requests.put('http://localhost:8008/flow/flow_http/json',data=json.dumps(flow_http))

flow_tcp_ssh1 = {'keys':'ipsource,ipdestination,tcpsourceport,tcpdestinationport,tcpflags','value':'bytes','filter':'ipdestination=10.0.0.3&tcpdestinationport=22&tcpflags=000000010','log':True}
requests.put('http://localhost:8008/flow/flow_tcp_ssh1/json',data=json.dumps(flow_tcp_ssh1))

flow_tcp_ssh2 = {'keys':'ipsource,ipdestination,tcpsourceport,tcpdestinationport,tcpflags','value':'bytes','filter':'ipdestination=10.0.0.4&tcpdestinationport=22&tcpflags=000000010','log':True}
requests.put('http://localhost:8008/flow/flow_tcp_ssh2/json',data=json.dumps(flow_tcp_ssh2))

flow_icmp1 = {'keys':'ipsource,ipdestination,icmptype','value':'bytes','filter':'ipdestination=10.0.0.3&icmptype=8','log':True}
requests.put('http://localhost:8008/flow/flow_icmp1/json',data=json.dumps(flow_icmp1))

flow_icmp2 = {'keys':'ipsource,ipdestination,icmptype','value':'bytes','filter':'ipdestination=10.0.0.4&icmptype=8','log':True}
requests.put('http://localhost:8008/flow/flow_icmp2/json',data=json.dumps(flow_icmp2))

r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_tcp_ssh1/json')
flow_tcp_ssh1=r.json()
global last1
last1=len(flow_tcp_ssh1)
global last_time1
last_time1=time.time()

r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_tcp_ssh2/json')
flow_tcp_ssh2=r.json()
global last2
last2=len(flow_tcp_ssh2)
global last_time2
last_time2=time.time()
while 1 == 1:
	r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_icmp1/json')
	flow_icmp1=r.json()
	i=0;
	for f in flow_icmp1:
		if f['value'] > line[7] :
			i=i+1;
	if i >= line[9]:
		temp=time.asctime()+" IMCP Warning "+f['key']
		f=open('log_icmp.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_icmp2/json')
	flow_icmp2=r.json()
	i=0
	for f in flow_icmp2:
		if f['value'] > line[7] :
			i=i+1;
	if i >= line[9]:
		temp=time.asctime()+" icmp Warning "+f['key']
		f=open('log_icmp.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_tcp_ssh1/json')
	flow_tcp_ssh1=r.json()
	current=len(flow_tcp_ssh1)
	if current>last1:		
		current_time=time.time()
		print last1,current
		print (current-last1)/(current_time-last_time1)
		if (current-last1)/(current_time-last_time1)> line[6]:
			temp=time.asctime()+" SSH Warning "+str(current-last2)+" "+str(round((current-last1)/(current_time-last_time1),2))
			f=open('log_ssh.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()
		last2=current
		last_time2=current_time
	r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_tcp_ssh2/json')
	flow_tcp_ssh2=r.json()
	current=len(flow_tcp_ssh2)
	if current>last2:		
		current_time=time.time()
		if (current-last2)/(current_time-last_time2)> line[6]:
			temp=time.asctime()+" SSH Warning "+str(current-last2)+" "+str(round((current-last2)/(current_time-last_time2),2))
			f=open('log_ssh.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()			
		last2=current
		last_time2=current_time
	r = requests.get('http://localhost:8008/activeflows/10.10.1.11/flow_http/json')
	flow_http=r.json()
	for f in flow_http:
		if line[8] in f['key'] and f['value'] > 40:
			temp=time.asctime()+" URL key word:"+"centos"+" "+f['key']
			f=open('log_http.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()
			break;
	pcpu_limit=line[1]
	var1=rrdtool.fetch(original_path+physical_name+'/cpu-0/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var2=rrdtool.fetch(original_path+physical_name+'/cpu-1/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var3=rrdtool.fetch(original_path+physical_name+'/cpu-2/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var4=rrdtool.fetch(original_path+physical_name+'/cpu-3/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	cpu0_used,cpu0_status=check_pcpu(var1,pcpu_limit)
	cpu1_used,cpu1_status=check_pcpu(var2,pcpu_limit)
	cpu2_used,cpu2_status=check_pcpu(var3,pcpu_limit)
	cpu3_used,cpu3_status=check_pcpu(var4,pcpu_limit)
	if cpu0_used > pcpu_limit and cpu0_used !='#':
		temp=time.asctime()+" CPU0 Waring "+str(cpu0_used)
		f=open('log_physical.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	if cpu1_used > pcpu_limit and cpu1_used !='#':
		temp=time.asctime()+" CPU1 Waring "+str(cpu1_used)
		f=open('log_physical.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	if cpu2_used > pcpu_limit and cpu2_used !='#':
		temp=time.asctime()+" CPU2 Waring "+str(cpu2_used)
		f=open('log_physical.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	if cpu3_used > pcpu_limit and cpu3_used !='#':
		temp=time.asctime()+" CPU3 Waring "+str(cpu3_used)
		f=open('log_physical.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	memory_limit=line[2]
	var1=rrdtool.fetch(original_path+physical_name+'/memory/memory-used.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var2=rrdtool.fetch(original_path+physical_name+'/memory/memory-free.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var3=rrdtool.fetch(original_path+physical_name+'/memory/memory-buffered.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var4=rrdtool.fetch(original_path+physical_name+'/memory/memory-cached.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var5=rrdtool.fetch(original_path+physical_name+'/memory/memory-slab_recl.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	var6=rrdtool.fetch(original_path+physical_name+'/memory/memory-slab_unrecl.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)  
        memory_used=check_mem(var1)
	memory_free=check_mem(var2)
	memory_buffered=check_mem(var3)
	memory_cached=check_mem(var4)
	memory_slab_r=check_mem(var5)
	memory_slab_u=check_mem(var6)		
	if memory_used!='#' and memory_free!='#' and memory_buffered!='#' and memory_cached!='#' and memory_slab_r!='#' and memory_slab_u!='#':
			memory_buffer_cache=memory_buffered+memory_cached+memory_slab_r+memory_slab_u
			memory_total=memory_used+memory_free+memory_buffered+memory_cached+memory_slab_r+memory_slab_u			
			memory_used_rate=round(memory_used/(memory_total)*100,2)
			if memory_used_rate > memory_limit:
				temp=time.asctime()+" Memory Warning "+str(memory_used_rate)
				f=open('log_physical.txt','a')
				f.write(temp)
				f.write('\n')
				f.close()
	load_limit=line[3]
	var1=rrdtool.fetch(original_path+physical_name+'/load/load.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
	load_s,load_m,load_l,load_status=check_tri(var1,load_limit)
	if load_m>load_limit and load_m!='#':
		temp=time.asctime()+" Load Warning "+str(load_m)
		f=open('log_physical.txt','a')
		f.write(temp)
		f.write('\n')
		f.close()
	vcpu_limit=line[4]
	vmemory_limit=line[5]
	var1=rrdtool.fetch(original_path+file[0]+'/virt-'+file[0]+'/virt_cpu_total.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)		
	var2=rrdtool.fetch(original_path+file[0]+'/virt-'+file[0]+'/virt_vcpu-0.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
	vcpu_total=check_single(var1)
        vcpu_0=check_single(var2)
	if vcpu_0!='#':
		vcpu_used=round(vcpu_0/vcpu_total*100,2)
		if vcpu_used > vcpu_limit:
			temp=time.asctime()+" "+file[0]+" CPU Warning "+str(vcpu_used)
			f=open('log_vm.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()
	var1=rrdtool.fetch(original_path+file[0]+'/virt-'+file[0]+'/memory-total.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	             
	var2=rrdtool.fetch(original_path+file[0]+'/virt-'+file[0]+'/memory-rss.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
	var3=rrdtool.fetch(original_path+file[0]+'/virt-'+file[0]+'/memory-actual_balloon.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
	vmemory_total=check_mem(var1)
	vmemory_rss=check_mem(var2)
        actual_balloon=check_mem(var3)
	if vmemory_rss!='#':
		vmemory_used=round(vmemory_rss/vmemory_total*100,2)
		if vmemory_used > vmemory_limit:
			temp=time.asctime()+" "+file[0]+" Memory Warning "+str(vmemory_used)
			f=open('log_vm.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()
	var1=rrdtool.fetch(original_path+file[1]+'/virt-'+file[1]+'/virt_cpu_total.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)		
	var2=rrdtool.fetch(original_path+file[1]+'/virt-'+file[1]+'/virt_vcpu-0.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
	vcpu_total=check_single(var1)
        vcpu_0=check_single(var2)
	if vcpu_0!='#':
		vcpu_used=round(vcpu_0/vcpu_total*100,2)
		if vcpu_used > vcpu_limit:
			temp=time.asctime()+" "+file[1]+" CPU Warning "+str(vcpu_used)
			f=open('log_vm.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()
	var1=rrdtool.fetch(original_path+file[1]+'/virt-'+file[1]+'/memory-total.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	             
	var2=rrdtool.fetch(original_path+file[1]+'/virt-'+file[1]+'/memory-rss.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
	var3=rrdtool.fetch(original_path+file[1]+'/virt-'+file[1]+'/memory-actual_balloon.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
	vmemory_total=check_mem(var1)
	vmemory_rss=check_mem(var2)
        actual_balloon=check_mem(var3)
	if vmemory_rss!='#':
		vmemory_used=round(vmemory_rss/vmemory_total*100,2)
		if vmemory_used > vmemory_limit:
			temp=time.asctime()+" "+file[1]+" Memory Warning "+str(vmemory_used)
			f=open('log_vm.txt','a')
			f.write(temp)
			f.write('\n')
			f.close()
	time.sleep(1)

	
