#coding:utf-8
from django.shortcuts import render
from django.template import Template,Context,RequestContext
from django.http import HttpResponse
from cloud.models import Threshold,User
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
import os
import sys
import rrdtool
import json
import requests
import time
import hashlib

original_path='/var/lib/collectd/rrd/'
start_time='-20s'
end_time='now'
CF='AVERAGE'
resolution='10s'

def check_pcpu(var,limit):
        if var[2][1][0] is not None:
                value1=round(100-var[2][1][0],2)
        elif var[2][0][0] is not None:
                value1=round(100-var[2][0][0],2)
        else:
                value1='*'

        if value1 == '*':
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
                value='*'
        return value
def check_single(var):
	if  var[2][1][0] is not None:
                value=var[2][1][0]
	elif var[2][0][0] is not None:
                value=var[2][0][0]
	else:
                value='*'
	return value
def check_double(var):
	if  var[2][1][0] is not None:
                value1=round(var[2][1][0],2)
                value2=round(var[2][1][1],2)
	elif var[2][0][0] is not None:
                value1=round(var[2][0][0],2)
                value2=round(var[2][0][1],2)
	else:
                value1='*'
		value2='*'
	return (value1,value2)
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
		value1='*'
		value2='*'
		value3='*'
	if value2!='*':
		if value2 < limit:
			value4="Normal"
		else:
			value4="Warning"
	else:
		value4="Unkown"
	return (value1,value2,value3,value4)
def index(request):
	username_s = request.POST.get('username','')
	password_s = request.POST.get('password','')
	if len(username_s)==0 or len(password_s)==0:
		return render(request,'index.html')
        pwdb=User.objects.filter(username=username_s)
	if len(pwdb)==0:
		status="账号不存在"
		return render(request,'index.html',{'status':status})
	p1=str(pwdb[0].password)
	myMd5=hashlib.md5()
	myMd5.update(password_s)
	p2=myMd5.hexdigest()
	if len(pwdb)==1 and p1==p2:
		request.session['username']=username_s
		return HttpResponseRedirect("monitor.html")
	else:
		status="密码错误"
		return render(request,'index.html',{'status':status})
def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect("/")
def home(request):
	th=Threshold.objects.get(id=1)
	A=request.get_full_path()[-3]
	B=request.get_full_path()[-1]
	if request.session.get('username') is None:
		return HttpResponseRedirect("/")
	if A=='1' and B=='1':
		global original_path	
		for filename in os.listdir(original_path):
		 	 if 'instance' not in filename:		
				physical_name=filename		
		pcpu_limit=th.pcpu
		var1=rrdtool.fetch(original_path+physical_name+'/cpu-0/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var2=rrdtool.fetch(original_path+physical_name+'/cpu-1/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var3=rrdtool.fetch(original_path+physical_name+'/cpu-2/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var4=rrdtool.fetch(original_path+physical_name+'/cpu-3/cpu-idle.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		cpu0_used,cpu0_status=check_pcpu(var1,pcpu_limit)
		cpu1_used,cpu1_status=check_pcpu(var2,pcpu_limit)
		cpu2_used,cpu2_status=check_pcpu(var3,pcpu_limit)
		cpu3_used,cpu3_status=check_pcpu(var4,pcpu_limit)
		memory_limit=th.pmem
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
		if memory_used!='*' and memory_free!='*' and memory_buffered!='*' and memory_cached!='*' and memory_slab_r!='*' and memory_slab_u!='*':
			memory_buffer_cache=memory_buffered+memory_cached+memory_slab_r+memory_slab_u
			memory_total=memory_used+memory_free+memory_buffered+memory_cached+memory_slab_r+memory_slab_u			
			memory_used_rate=round(memory_used/(memory_total)*100,2)
			if memory_used_rate < memory_limit:
				memory_status="Normal"
			else:
				memory_status="Warning"
		else:
			memory_buffer_cache='*'
			memory_total='*'
			memory_used_rate='*'
			memory_status="Unkown"
		var1=rrdtool.fetch(original_path+physical_name+'/interface-p1p2/if_octets.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var2=rrdtool.fetch(original_path+physical_name+'/interface-p1p2/if_packets.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
                octets_rx,octets_tx=check_double(var1)
                packets_rx,packets_tx=check_double(var2)
		var1=rrdtool.fetch(original_path+physical_name+'/disk-sda/disk_ops.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var2=rrdtool.fetch(original_path+physical_name+'/disk-sda/disk_octets.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)        
                disk_ops_read,disk_ops_write=check_double(var1)          
                disk_octets_read,disk_octets_write=check_double(var2)
		load_limit=th.pload
		var1=rrdtool.fetch(original_path+physical_name+'/load/load.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		load_s,load_m,load_l,load_status=check_tri(var1,load_limit)
		c = Context({'physical_name':physical_name,'cpu0_used':cpu0_used,'cpu0_status':cpu0_status,'cpu1_used':cpu1_used,'cpu1_status':cpu1_status,'cpu2_used':cpu2_used,'cpu2_status':cpu2_status,'cpu3_used':cpu3_used,'cpu3_status':cpu3_status,'pcpu_limit':pcpu_limit,'memory_total':memory_total,'memory_used':memory_used,'memory_free':memory_free,'memory_buffer_cache':memory_buffer_cache,'memory_used_rate':memory_used_rate,'memory_limit':memory_limit,'memory_status':memory_status,'octets_tx':octets_tx,'octets_rx':octets_rx,'packets_tx':packets_tx,'packets_rx':packets_rx,'disk_ops_read':disk_ops_read,'disk_ops_write':disk_ops_write,'disk_octets_read':disk_octets_read,'disk_octets_write':disk_octets_write,'load_s':load_s,'load_m':load_m,'load_l':load_l,'load_limit':load_limit,'load_status':load_status})
		print type(c)
		return render(request,'monitor.html',c)
	elif A=='2':
		file=os.listdir(original_path)
		file.sort()  
		if B=='1':
			vm_name=file[0]
		elif B=='2':
			vm_name=file[1]
		vcpu_limit=th.vcpu
		vcpu_used='*'
		var1=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/virt_cpu_total.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)		
		var2=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/virt_vcpu-0.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
		vcpu_total=check_single(var1)
                vcpu_0=check_single(var2)
		if vcpu_0!='*':
			vcpu_used=round(vcpu_0/vcpu_total*100,2)
			if vcpu_used < vcpu_limit:
				vcpu_status="Normal"
			else:
				vcpu_status="Warning"
		else:
			vcpu_status="Unkown"
  		vmemory_limit=th.vmem
		var1=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/memory-total.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	             
		var2=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/memory-rss.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	
		var3=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/memory-actual_balloon.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)	

		vmemory_total=check_mem(var1)
		vmemory_rss=check_mem(var2)
                actual_balloon=check_mem(var3)
		if vmemory_rss!='*':
			vmemory_used=round(vmemory_rss/vmemory_total*100,2)
			if vmemory_used < vmemory_limit:
				vmemory_status="Normal"
			else:
				vmemory_status="Warning"
		else:
			vmemory_used='*'
			vmemory_status="Unkown"
		for child in os.listdir(original_path+vm_name+'/virt-'+vm_name):
				if "packets" in child:
					tag=child[11:25]
					break;
		var1=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/if_octets-'+tag+'.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var2=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/if_packets-'+tag+'.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
                voctets_rx,voctets_tx=check_double(var1)
		vpackets_rx,vpackets_tx=check_double(var2)
		var1=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/disk_ops-vda.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
		var2=rrdtool.fetch(original_path+vm_name+'/virt-'+vm_name+'/disk_octets-vda.rrd',CF,'-r',resolution,'-s',start_time,'-e',end_time)
                vdisk_ops_read,vdisk_ops_write=check_double(var1)
                vdisk_octets_read,vdisk_octets_write=check_double(var2)
		c=Context({'vm_name':vm_name,'vcpu_total':vcpu_total,'vcpu_0':vcpu_0,'vcpu_used':vcpu_used,'vcpu_limit':vcpu_limit,'vcpu_status':vcpu_status,'vmemory_total':vmemory_total,'vmemory_rss':vmemory_rss,'actual_balloon':actual_balloon,'vmemory_used':vmemory_used,'vmemory_limit':vmemory_limit,'vmemory_status':vmemory_status,'if_name':tag,'voctets_rx':voctets_rx,'voctets_tx':voctets_tx,'vpackets_rx':vpackets_rx,'vpackets_tx':vpackets_tx,'vdisk_ops_read':vdisk_ops_read,'vdisk_ops_write':vdisk_ops_write,'vdisk_octets_read':vdisk_octets_read,'vdisk_octets_write':vdisk_octets_write})
		return render(request,'monitor.html',c)	
	elif A=='3':
		r=requests.get('http://localhost:8008/agents/json')
		agents=r.json()
		if len(agents) == 0:
			return render(request,'monitor.html')
		temp=str(agents.keys()[0])
		r=requests.get('http://localhost:8008/metric/'+temp+'/json')
		metric=r.json()
		listp=[]
		for m in metric.keys():
	        	if 'ifname' in m:
               			 listp.append((str(m),str(metric.get(m))))
		listp.sort()
		original_path='/var/lib/collectd/rrd/'
		file=os.listdir(original_path)
		file.sort()
		lists=[]
		for f in file:
			if 'instance' in f:
                		for child in os.listdir(original_path+f+'/virt-'+f):
                        		if "packets" in child:
                                		tap=child[11:25]
                                		tag=child[14:25]
                                		lists.append((f,tap,tag))
		if B=='1':
			r=requests.get('http://localhost:8008/activeflows/'+temp+'/flow_tcp/json')
			flow_tcp=r.json()
			list_tcp=[]
			for flow in flow_tcp:
				if flow.get('value') > 10:
					f=str(flow.get('key')).split(',')
					f.insert(0,time.strftime("%H:%M:%S"))
					f.append(round(flow.get('value'),2))
					list_tcp.append(f)
			c=Context({'listp':listp,'lists':lists,'list_tcp':list_tcp})
			return render(request,'monitor.html',c)
		elif B=='2':
			r=requests.get('http://localhost:8008/activeflows/'+temp+'/flow_udp/json')
			flow_udp=r.json()
			list_udp=[]
			for flow in flow_udp:
				if flow.get('value') > 10:
					f=str(flow.get('key')).split(',')
					f.insert(0,time.strftime("%H:%M:%S"))
					f.append(round(flow.get('value'),2))
					list_udp.append(f)
			c=Context({'listp':listp,'lists':lists,'list_udp':list_udp})
			return render(request,'monitor.html',c)
		elif B=='3':
			r=requests.get('http://localhost:8008/activeflows/'+temp+'/flow_icmp/json')
			flow_icmp=r.json()
			list_icmp=[]
			for flow in flow_icmp:
				if flow.get('value') > 10:
					f=str(flow.get('key')).split(',')
					f.insert(0,time.strftime("%H:%M:%S"))
					f.append(round(flow.get('value'),2))
					list_icmp.append(f)
			c=Context({'listp':listp,'lists':lists,'list_icmp':list_icmp})
			return render(request,'monitor.html',c)
		elif B=='4':
			r=requests.get('http://localhost:8008/activeflows/'+temp+'/flow_http/json')
			flow_http=r.json()
			list_http=[]
			for flow in flow_http:
				if flow.get('value') > 10:
					f=str(flow.get('key')).split(',')
					f.insert(0,time.strftime("%H:%M:%S"))
					f.append(round(flow.get('value'),2))
					list_http.append(f)
			c=Context({'listp':listp,'lists':lists,'list_http':list_http})
			return render(request,'monitor.html',c)
	elif A=='4':
		if B=='1':
			filename="/home/foll/MiaoFaBiao/mysite/cloud/log_physical.txt"
		elif B=='2':
			filename="/home/foll/MiaoFaBiao/mysite/cloud/log_vm.txt"
		elif B=='3':
			filename="/home/foll/MiaoFaBiao/mysite/cloud/log_ssh.txt"
		elif B=='4':
			filename="/home/foll/MiaoFaBiao/mysite/cloud/log_icmp.txt"
		elif B=='5':
			filename="/home/foll/MiaoFaBiao/mysite/cloud/log_http.txt"
		f=open(filename)
		list_s=f.readlines()
		list_s.reverse()
		list_security=list_s[0:15]
		c=Context({'list_security':list_security})
		return render(request,'monitor.html',c)
	elif A=='5' and B=='1':
		list_threshold=[];
		list_threshold.append(th.pcpu)
		list_threshold.append(th.pmem)
		list_threshold.append(th.pload)
		list_threshold.append(th.vcpu)
		list_threshold.append(th.vmem)
		list_threshold.append(th.sshtv)
		list_threshold.append(th.icmptv)
		list_threshold.append(th.icmpntv)
		list_threshold.append(th.keyword)
		c=Context({'list_threshold':list_threshold})
		return render_to_response('monitor.html',c,context_instance=RequestContext(request))
	else:
		password_1 = request.POST.get('pwd1','')
		password_2 = request.POST.get('pwd2','')
		password_3 = request.POST.get('pwd3','')
		print password_1,password_2,password_3
		return render(request,'monitor.html') 


