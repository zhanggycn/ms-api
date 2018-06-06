# author: zhanggy.cn
# makefile of ms-api_2018-06-05 in beijing

proj_server := "app.py"
proj_path := $(shell pwd)

install:
		pip install  -r requirements.txt

clean:
		find . -name \*.pyc -delete

dev:
		cd $(proj_path)/api && \
		python $(proj_server)

test:
		cd $(proj_path)/api && \
		py.test -q ../tests/test-view.py
