#!/bin/bash
COLLECTER_IP=10.10.1.12
COLLECTER_PORT=6343
AGENT_IP=p1p2
HEADER_BYTES=128
SAMPLING_N=1
POLLING_SECS=30
ovs-vsctl -- --id=@s create sflow agent=${AGENT_IP} target=\"${COLLECTER_IP}:${COLLECTER_PORT}\" header=${HEADER_BYTES} sampling=${SAMPLING_N} polling=${POLLING_SECS} -- set bridge br-int sflow=@s
ovs-vsctl list sflow

