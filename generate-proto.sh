#!/bin/bash

protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/rb_announcement.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/company.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/person.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/trade.proto

protoc --proto_path=proto --descriptor_set_out=build/gen/student/academic/v1/all.fdset proto/student/academic/v1/*
