{{ define "elasticsearch_check" -}}
- name: {{ .Chart.Name }}-elasticsearch-check
  image: byrnedo/alpine-curl
  command:
  - 'sh'
  - '-c'
  - 'until curl {{ .Chart.Name }}-elasticsearch:{{ .Values.elasticsearch.port }}; do echo waiting for elasticsearch pod; sleep 2; done;'
{{ end }}

---

{{ define "elasticsearch_populate" -}}
- name: {{ .Chart.Name }}-elasticsearch-populate
  image: {{ .Values.deploy.ecr }}{{ .Chart.Name }}-init:{{ .Values.deploy.imageTag }}
  command: ["populate-elasticsearch"]
  envFrom:
    - configMapRef:
        name: {{ .Chart.Name }}
{{ end }}
