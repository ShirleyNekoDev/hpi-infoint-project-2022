#!/bin/bash

protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/rb_announcement.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/rb_company.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/rb_person.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/ffb_trade.proto
protoc --proto_path=proto --python_out=build/gen proto/student/academic/v1/ffb_company.proto

protoc --proto_path=proto --descriptor_set_out=build/gen/student/academic/v1/all.fdset proto/student/academic/v1/*
