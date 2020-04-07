# Include this template in a container if you wish it to be used for readiness probes.
# The readiness probe stops traffic to this pod if it is not ready, then resumes when
# it is detected as ready again.

{{ define "readiness" -}}

readinessProbe:
  httpGet:
    path: /ping
    port: {{ .http.httpPort }}
  initialDelaySeconds: {{ .readiness.initialDelay }}
  periodSeconds: {{ .readiness.period }}

{{ end }}
