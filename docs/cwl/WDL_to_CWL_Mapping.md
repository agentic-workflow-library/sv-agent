# WDL to CWL Conversion Mapping

This document details the conversion decisions made when translating PloidyEstimation.wdl to CWL.

## Structural Mapping

### Workflow Definition

**WDL:**
```wdl
workflow Ploidy {
  input { ... }
  call BuildPloidyMatrix { ... }
  call PloidyScore { ... }
  output { ... }
}
```

**CWL:**
```yaml
class: Workflow
inputs: { ... }
steps:
  build_ploidy_matrix:
    run: BuildPloidyMatrix.cwl
  ploidy_score:
    run: PloidyScore.cwl
outputs: { ... }
```

### Type System

| WDL Type | CWL Type | Notes |
|----------|----------|-------|
| `File` | `File` | Direct mapping |
| `String` | `string` | Direct mapping |
| `Int` | `int` | Direct mapping |
| `RuntimeAttr` | Custom schema | Defined in RuntimeAttr.yml |
| `RuntimeAttr?` | `RuntimeAttr?` | Nullable type preserved |

### Runtime Attributes

**WDL Pattern:**
```wdl
RuntimeAttr default_attr = object {
  cpu_cores: 1,
  mem_gb: 3.75,
  disk_gb: 50
}
RuntimeAttr runtime_attr = select_first([runtime_attr_override, default_attr])
```

**CWL Pattern:**
```yaml
ResourceRequirement:
  coresMin: $(inputs.runtime_attr_override.cpu_cores || 1)
  ramMin: $(inputs.runtime_attr_override.mem_gb || 3.75) * 1024
  outdirMin: $(inputs.runtime_attr_override.disk_gb || 50) * 1024
```

### Command Generation

**WDL:**
```wdl
command <<<
  set -euo pipefail
  zcat ~{bincov_matrix} | awk '...' | bgzip > ~{batch}_ploidy_matrix.bed.gz
>>>
```

**CWL:**
```yaml
arguments:
  - shellQuote: false
    valueFrom: |
      set -euo pipefail
      zcat $(inputs.bincov_matrix.path) | awk '...' | bgzip > $(inputs.batch)_ploidy_matrix.bed.gz
```

## Key Conversion Patterns

### 1. Variable Interpolation
- WDL: `~{variable}` → CWL: `$(inputs.variable)`
- WDL: `${variable}` → CWL: `$(inputs.variable)`

### 2. Default Values
- WDL: Defined in task with `select_first()`
- CWL: JavaScript expressions with `||` operator

### 3. File Paths
- WDL: Direct file reference
- CWL: `$(inputs.file.path)` for file objects

### 4. Docker Configuration
- WDL: `docker:` in runtime block
- CWL: `DockerRequirement` with `dockerPull`

### 5. Output Capture
- WDL: `output { File x = "filename" }`
- CWL: `outputs:` with `glob` patterns

## Complex AWK Script Preservation

The AWK script in BuildPloidyMatrix performs bin aggregation:
- Preserved exactly as written
- Proper escaping of backslashes in CWL
- Shell interpretation via `ShellCommandRequirement`

## Workflow Connectivity

**WDL:**
```wdl
call PloidyScore {
  input:
    ploidy_matrix = BuildPloidyMatrix.ploidy_matrix
}
```

**CWL:**
```yaml
ploidy_score:
  in:
    ploidy_matrix: build_ploidy_matrix/ploidy_matrix
```

## Resource Management

The conversion maintains resource flexibility:
- Optional runtime overrides preserved
- Default values embedded in CWL
- Cloud-platform agnostic (no preemptible in CWL)

## Validation & Testing

CWL provides stronger validation:
- Schema validation for custom types
- Built-in type checking
- Tool validation before execution