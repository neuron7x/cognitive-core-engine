import yaml, pathlib; y=yaml.safe_load(open('.github/workflows/ci.yml','r',encoding='utf-8')); assert 'jobs'in y
