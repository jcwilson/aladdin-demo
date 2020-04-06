{{ define "redis_check" -}}
- name: {{ .Chart.Name }}-redis-check
  image: busybox
  command:
  - 'sh'
  - '-c'
  - 'until nslookup {{ .Chart.Name }}-redis; do echo waiting for redis pod; sleep 2; done;'
{{ end }}

---

{{ define "redis_populate" -}}
- name: {{ .Chart.Name }}-redis-populate
  image: {{ .Values.deploy.ecr }}{{ .Chart.Name }}-commands:{{ .Values.deploy.imageTag }}
  command:
  - 'python'
  - 'shared/redis_util/redis_populate.py'
  envFrom:
    - configMapRef:
        name: {{ .Chart.Name }}
{{ end }}
