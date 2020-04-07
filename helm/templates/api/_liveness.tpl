# Include this template in a container if you wish it to be used for liveness probes.
# The liveness probe terminates and restarts the pod if it's unhealthy.


{{ define "liveness" -}}

livenessProbe:
  httpGet:
    path: /ping
    port: {{ .http.httpPort }}
  initialDelaySeconds: {{ .liveness.initialDelay }}
  periodSeconds: {{ .liveness.period }}

{{ end }}
