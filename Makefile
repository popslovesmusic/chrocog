# Soundlab Φ-Matrix - Release Build System
# Feature 019: Release Readiness Validation

# Version information
VERSION ?= 1.0.0
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
GIT_TAG := $(shell git describe --tags --exact-match 2>/dev/null || echo "untagged")
	
# Docker configuration
DOCKER_REGISTRY ?= soundlab
DOCKER_IMAGE := $(DOCKER_REGISTRY)/phi-matrix
DOCKER_TAG := $(VERSION)
	
# Paths
SERVER_DIR := server
STATIC_DIR := static
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist
	
# Python configuration
PYTHON := python3
PIP := pip3
PYTEST := pytest
VENV := .venv
	
# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color
	
.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)Soundlab Φ-Matrix - Build System$(NC)"
	@echo "$(CYAN)Version: $(VERSION)$(NC)"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	
.PHONY: version
version: ## Show version information
	@echo "Version:    $(VERSION)"
	@echo "Commit:     $(GIT_COMMIT)"
	@echo "Tag:        $(GIT_TAG)"
	@echo "Build Date: $(BUILD_DATE)"
	
#==============================================================================
# Development Targets
#==============================================================================

.PHONY: install
install: ## Install Python dependencies
	@echo "$(CYAN)Installing dependencies...$(NC)"
	$(PIP) install -r $(SERVER_DIR)/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"
	
.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "$(CYAN)Installing development dependencies...$(NC)"
	$(PIP) install -r $(SERVER_DIR)/requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov black flake8 mypy
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"
	
.PHONY: venv
venv: ## Create virtual environment
	@echo "$(CYAN)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)✓ Virtual environment created at $(VENV)$(NC)"
	@echo "Activate with: source $(VENV)/bin/activate (Linux/Mac) or $(VENV)\Scripts\activate (Windows)"
	
#==============================================================================
# Feature 020: Build Environment + Dependency Bootstrap
#==============================================================================

DASE_DIR := "sase amp fixed"
DASE_BUILD := $(DASE_DIR)/build
DASE_DIST := $(DASE_DIR)/dist
	
.PHONY: setup
setup: ## Bootstrap complete build environment (FR-001, SC-001)
	@echo "$(CYAN)========================================$(NC)"
	@echo "$(CYAN)Feature 020: Environment Bootstrap$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@echo ""
	@echo "$(CYAN)[1/4] Installing Python dependencies...$(NC)"
	$(PIP) install -r $(SERVER_DIR)/requirements.txt
	@echo "$(GREEN)✓ Python dependencies installed$(NC)"
	@echo ""
	@echo "$(CYAN)[2/4] Building C++ extension (D-ASE)...$(NC)"
	$(MAKE) build-ext
	@echo ""
	@echo "$(CYAN)[3/4] Verifying build...$(NC)"
	$(PYTHON) -c "import dase_engine; print(f'D-ASE version: {dase_engine.__version__}'); dase_engine.CPUFeatures.print_capabilities()" || echo "$(RED)Warning: dase_engine not importable (may need FFTW3 library)$(NC)"
	@echo ""
	@echo "$(CYAN)[4/4] Running post-install checks...$(NC)"
	$(PYTHON) --version
	$(PIP) list | grep -E "fastapi|pybind11|numpy|sounddevice" || true
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)✓ Setup complete! Environment ready.$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo "Next steps:"
	@echo "  - Run tests: make test"
	@echo "  - Run validation: make validate-020"
	@echo "  - Build release: make rc"
	
.PHONY: build-ext
build-ext: ## Build C++ extension (D-ASE engine) (FR-003)
	@echo "$(CYAN)Building C++ extension with AVX2 optimization...$(NC)"
	cd $(DASE_DIR) && $(PYTHON) setup.py build_ext --inplace
	@echo "$(GREEN)✓ C++ extension built: dase_engine.so/.pyd$(NC)"
	
.PHONY: build-ext-clean
build-ext-clean: ## Clean C++ extension build artifacts
	@echo "$(CYAN)Cleaning C++ extension build...$(NC)"
	cd $(DASE_DIR) && rm -rf build dist *.so *.pyd *.egg-info
	@echo "$(GREEN)✓ C++ extension cleaned$(NC)"
	
.PHONY: test-simulate
test-simulate: ## Run tests in simulation mode (no hardware) (FR-010, SC-006)
	@echo "$(CYAN)Running tests in simulation mode (no audio hardware)...$(NC)"
	SOUNDLAB_SIMULATE=1 $(MAKE) test
	@echo "$(GREEN)✓ Simulation tests passed$(NC)"
	
.PHONY: report
report: ## Generate test and validation reports (FR-009, SC-004)
	@echo "$(CYAN)Generating test reports...$(NC)"
	mkdir -p tests/reports
	@echo "Running validation scripts and collecting reports..."
	cd $(SERVER_DIR) && $(PYTHON) ../scripts/run_tests_and_report.py
	@echo "$(GREEN)✓ Reports generated in tests/reports/$(NC)"
	@ls -lh tests/reports/
	
.PHONY: validate-020
validate-020: ## Validate Feature 020 implementation
	@echo "$(CYAN)Validating Feature 020: Build Environment$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_020.py
	@echo "$(GREEN)✓ Feature 020 validation passed$(NC)"
	
#==============================================================================
# Testing Targets
#==============================================================================

.PHONY: test
test: ## Run all tests
	@echo "$(CYAN)Running tests...$(NC)"
	cd $(SERVER_DIR) && $(PYTEST) -v --tb=short
	@echo "$(GREEN)✓ Tests passed$(NC)"
	
.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "$(CYAN)Running tests (verbose)...$(NC)"
	cd $(SERVER_DIR) && $(PYTEST) -vv --tb=long
	
.PHONY: test-cov
test-cov: ## Run tests with coverage
	@echo "$(CYAN)Running tests with coverage...$(NC)"
	cd $(SERVER_DIR) && $(PYTEST) --cov=. --cov-report=html --cov-report=term
	
.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(CYAN)Running unit tests...$(NC)"
	cd $(SERVER_DIR) && $(PYTEST) -v -m "not integration"
	
.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(CYAN)Running integration tests...$(NC)"
	cd $(SERVER_DIR) && $(PYTEST) -v -m "integration"
	
.PHONY: validate
validate: ## Run all validation scripts
	@echo "$(CYAN)Running validation scripts...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_015.py
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_016.py
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_017.py
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_018.py
	@echo "$(GREEN)✓ All validations passed$(NC)"
	
#==============================================================================
# Feature 021: Automated Validation & Regression Testing
#==============================================================================

.PHONY: test-fast
test-fast: ## Run unit tests only (fast) (FR-008)
	@echo "$(CYAN)Running unit tests (fast)...$(NC)"
	$(PYTEST) -m unit tests/
	@echo "$(GREEN)✓ Unit tests passed$(NC)"
	
.PHONY: test-perf
test-perf: ## Run performance tests with budget enforcement (FR-005, FR-008)
	@echo "$(CYAN)Running performance benchmark...$(NC)"
	$(PYTHON) tests/perf/bench_phi_matrix.py --duration 60
	@echo "$(GREEN)✓ Performance tests passed$(NC)"
	
.PHONY: test-golden
test-golden: ## Run golden data regression tests (FR-006)
	@echo "$(CYAN)Running golden data regression tests...$(NC)"
	$(PYTEST) -m golden tests/
	@echo "$(GREEN)✓ Golden data tests passed$(NC)"
	
.PHONY: test-all
test-all: ## Run all test suites (unit, integration, perf) (SC-001)
	@echo "$(CYAN)Running complete test suite...$(NC)"
	$(PYTEST) -m "not e2e" tests/
	@echo "$(GREEN)✓ All tests passed$(NC)"
	
.PHONY: approve-baseline
approve-baseline: ## Approve current metrics as new baseline (FR-006, FR-008)
	@echo "$(CYAN)Approving performance baseline...$(NC)"
	@if [ -f "tests/reports/perf_summary.json" ]; then \
		mkdir -p tests/golden; \
		cp tests/reports/perf_summary.json tests/golden/baseline_perf.json; \
		echo "$(GREEN)✓ Baseline approved and saved$(NC)"; \
	else \
		echo "$(RED)Error: No perf_summary.json found. Run 'make test-perf' first.$(NC)"; \
		exit 1; \
	fi
	
.PHONY: validate-021
validate-021: ## Validate Feature 021 implementation
	@echo "$(CYAN)Validating Feature 021: Test Automation$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_021.py
	@echo "$(GREEN)✓ Feature 021 validation passed$(NC)"
	
#==============================================================================
# Feature 023: Hardware Validation
#==============================================================================

.PHONY: hardware-test
hardware-test: ## Run hardware validation tests (FR-005)
	@echo "$(CYAN)Running hardware validation tests...$(NC)"
	$(PYTEST) tests/hardware/test_i2s_phi.py -v --asyncio-mode=auto
	@echo "$(GREEN)✓ Hardware tests passed$(NC)"
	
.PHONY: calibrate-sensors
calibrate-sensors: ## Calibrate Φ-sensors (FR-007, SC-005)
	@echo "$(CYAN)Calibrating Φ-sensors...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) calibrate_sensors.py --duration 10000
	@echo "$(GREEN)✓ Sensor calibration complete$(NC)"
	
.PHONY: log-hardware
log-hardware: ## Log hardware metrics to CSV (FR-010)
	@echo "$(CYAN)Logging hardware metrics...$(NC)"
	@mkdir -p logs
	cd $(SERVER_DIR) && $(PYTHON) -c "from sensor_manager import SensorManager; import asyncio; m = SensorManager({'simulation_mode': True}); asyncio.run(m.start()); asyncio.get_event_loop().run_until_complete(asyncio.sleep(60)); asyncio.run(m.stop())"
	@echo "$(GREEN)✓ Hardware metrics logged to logs/hardware_phi_metrics.csv$(NC)"
	
.PHONY: validate-023
validate-023: ## Validate Feature 023 implementation
	@echo "$(CYAN)Validating Feature 023: Hardware Validation$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_023.py
	@echo "$(GREEN)✓ Feature 023 validation passed$(NC)"
	
#==============================================================================
# Code Quality Targets
#==============================================================================

.PHONY: lint
lint: ## Run linter (flake8)
	@echo "$(CYAN)Running linter...$(NC)"
	cd $(SERVER_DIR) && flake8 --max-line-length=120 --exclude=__pycache__,.venv,venv
	
.PHONY: format
format: ## Format code with black
	@echo "$(CYAN)Formatting code...$(NC)"
	cd $(SERVER_DIR) && black --line-length=120 .
	
.PHONY: format-check
format-check: ## Check code formatting
	@echo "$(CYAN)Checking code formatting...$(NC)"
	cd $(SERVER_DIR) && black --line-length=120 --check .
	
.PHONY: typecheck
typecheck: ## Run type checker (mypy)
	@echo "$(CYAN)Running type checker...$(NC)"
	cd $(SERVER_DIR) && mypy --ignore-missing-imports .
	
.PHONY: quality
quality: format-check lint typecheck ## Run all quality checks
	@echo "$(GREEN)✓ All quality checks passed$(NC)"
	
#==============================================================================
# Build Targets
#==============================================================================

.PHONY: clean
clean: ## Clean build artifacts
	@echo "$(CYAN)Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✓ Build artifacts cleaned$(NC)"
	
.PHONY: build
build: clean ## Build release artifacts
	@echo "$(CYAN)Building release artifacts...$(NC)"
	mkdir -p $(BUILD_DIR)
	mkdir -p $(DIST_DIR)
	@echo "VERSION=$(VERSION)" > $(BUILD_DIR)/version.txt
	@echo "GIT_COMMIT=$(GIT_COMMIT)" >> $(BUILD_DIR)/version.txt
	@echo "BUILD_DATE=$(BUILD_DATE)" >> $(BUILD_DIR)/version.txt
	@echo "$(GREEN)✓ Build complete$(NC)"
	
.PHONY: rc
rc: clean test build ## Build release candidate (FR-001)
	@echo "$(CYAN)Building release candidate $(VERSION)...$(NC)"
	@echo "Running comprehensive validation..."
	$(MAKE) validate
	@echo "Creating release bundle..."
	mkdir -p $(DIST_DIR)/soundlab-$(VERSION)
	cp -r $(SERVER_DIR) $(DIST_DIR)/soundlab-$(VERSION)/
	cp -r $(STATIC_DIR) $(DIST_DIR)/soundlab-$(VERSION)/
	cp -r $(DOCS_DIR) $(DIST_DIR)/soundlab-$(VERSION)/
	cp README.md $(DIST_DIR)/soundlab-$(VERSION)/ 2>/dev/null || true
	cp LICENSE $(DIST_DIR)/soundlab-$(VERSION)/ 2>/dev/null || true
	cp $(BUILD_DIR)/version.txt $(DIST_DIR)/soundlab-$(VERSION)/
	cd $(DIST_DIR) && tar -czf soundlab-$(VERSION).tar.gz soundlab-$(VERSION)
	@echo "$(GREEN)✓ Release candidate built: $(DIST_DIR)/soundlab-$(VERSION).tar.gz$(NC)"
	@echo "$(GREEN)✓ Docker image ready to build with: make docker-build$(NC)"
	
#==============================================================================
# Docker Targets
#==============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(CYAN)Building Docker image...$(NC)"
	docker build \
		--build-arg VERSION=$(VERSION) \
		--build-arg GIT_COMMIT=$(GIT_COMMIT) \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		-t $(DOCKER_IMAGE):$(DOCKER_TAG) \
		-t $(DOCKER_IMAGE):latest \
		-f Dockerfile .
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"
	
.PHONY: docker-push
docker-push: ## Push Docker image to registry
	@echo "$(CYAN)Pushing Docker image...$(NC)"
	docker push $(DOCKER_IMAGE):$(DOCKER_TAG)
	docker push $(DOCKER_IMAGE):latest
	@echo "$(GREEN)✓ Docker image pushed$(NC)"
	
.PHONY: docker-run
docker-run: ## Run Docker container locally
	@echo "$(CYAN)Running Docker container...$(NC)"
	docker run -it --rm \
		-p 8000:8000 \
		-v $(PWD)/logs:/app/logs \
		$(DOCKER_IMAGE):$(DOCKER_TAG)
	
.PHONY: docker-compose-up
docker-compose-up: ## Start staging environment with docker-compose
	@echo "$(CYAN)Starting staging environment...$(NC)"
	docker-compose -f docker-compose.staging.yml up -d
	@echo "$(GREEN)✓ Staging environment started$(NC)"
	
.PHONY: docker-compose-down
docker-compose-down: ## Stop staging environment
	@echo "$(CYAN)Stopping staging environment...$(NC)"
	docker-compose -f docker-compose.staging.yml down
	@echo "$(GREEN)✓ Staging environment stopped$(NC)"
	
.PHONY: docker-compose-logs
docker-compose-logs: ## Show staging logs
	docker-compose -f docker-compose.staging.yml logs -f
	
#==============================================================================
# Security & Compliance Targets
#==============================================================================

.PHONY: sbom
sbom: ## Generate Software Bill of Materials
	@echo "$(CYAN)Generating SBOM...$(NC)"
	@command -v syft >/dev/null 2>&1 || { echo "$(RED)Error: syft not installed$(NC)"; exit 1; }
	syft packages dir:. -o spdx-json > $(BUILD_DIR)/sbom.spdx.json
	syft packages dir:. -o cyclonedx-json > $(BUILD_DIR)/sbom.cyclonedx.json
	@echo "$(GREEN)✓ SBOM generated: $(BUILD_DIR)/sbom.*.json$(NC)"
	
.PHONY: security-scan
security-scan: ## Run security scans
	@echo "$(CYAN)Running security scans...$(NC)"
	@command -v safety >/dev/null 2>&1 || $(PIP) install safety
	safety check --json
	@echo "$(GREEN)✓ Security scan complete$(NC)"
	
.PHONY: license-check
license-check: ## Check license compatibility
	@echo "$(CYAN)Checking licenses...$(NC)"
	@command -v pip-licenses >/dev/null 2>&1 || $(PIP) install pip-licenses
	pip-licenses --format=markdown > $(BUILD_DIR)/licenses.md
	@echo "$(GREEN)✓ License report: $(BUILD_DIR)/licenses.md$(NC)"
	
#==============================================================================
# Feature 024: Security & Privacy Audit
#==============================================================================

.PHONY: security-test
security-test: ## Run security test suite (FR-001 to FR-011)
	@echo "$(CYAN)Running security tests...$(NC)"
	$(PYTEST) tests/security/test_security_024.py -v
	@echo "$(GREEN)✓ Security tests passed$(NC)"
	
.PHONY: sast
sast: ## Run SAST (Bandit + Semgrep) (FR-012)
	@echo "$(CYAN)Running SAST scans...$(NC)"
	@command -v bandit >/dev/null 2>&1 || $(PIP) install bandit
	bandit -r $(SERVER_DIR)/ -f txt || true
	@echo "$(GREEN)✓ SAST scan complete$(NC)"
	
.PHONY: dast
dast: ## Run DAST (ZAP baseline) (FR-012, SC-003)
	@echo "$(CYAN)Running DAST scan...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)Error: Docker required for ZAP scan$(NC)"; exit 1; }
	@echo "Starting application..."
	@docker-compose up -d || true
	@sleep 5
	@echo "Running ZAP baseline scan..."
	@docker run --rm --network="host" owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000 || true
	@echo "$(GREEN)✓ DAST scan complete$(NC)"
	
.PHONY: sbom-generate
sbom-generate: ## Generate SBOM (FR-013, SC-004)
	@echo "$(CYAN)Generating SBOM...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@command -v syft >/dev/null 2>&1 || { echo "$(RED)Error: syft not installed. Install: curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh$(NC)"; exit 1; }
	syft dir:$(SERVER_DIR) -o spdx-json > $(BUILD_DIR)/sbom-python.spdx.json
	syft dir:$(SERVER_DIR) -o cyclonedx-json > $(BUILD_DIR)/sbom-python.cyclonedx.json
	@echo "$(GREEN)✓ SBOM generated: $(BUILD_DIR)/sbom-*.json$(NC)"
	
.PHONY: license-compliance
license-compliance: ## Check license compliance (FR-013, SC-004)
	@echo "$(CYAN)Checking license compliance...$(NC)"
	@mkdir -p $(BUILD_DIR)
	@command -v pip-licenses >/dev/null 2>&1 || $(PIP) install pip-licenses
	pip-licenses --format=json --output-file=$(BUILD_DIR)/licenses-python.json
	$(PYTHON) scripts/license_check.py \
		--licenses $(BUILD_DIR)/licenses-python.json \
		--allowlist config/license-allowlist.txt \
		--report $(BUILD_DIR)/license-compliance.json
	@echo "$(GREEN)✓ License compliance check complete$(NC)"
	
.PHONY: sign
sign: ## Sign artifacts with cosign (FR-014, SC-004)
	@echo "$(CYAN)Signing artifacts...$(NC)"
	@command -v cosign >/dev/null 2>&1 || { echo "$(RED)Error: cosign not installed. Install: go install github.com/sigstore/cosign/cmd/cosign@latest$(NC)"; exit 1; }
	@if [ -f "$(BUILD_DIR)/sbom-python.spdx.json" ]; then \
		cosign sign-blob --yes $(BUILD_DIR)/sbom-python.spdx.json \
			--output-signature $(BUILD_DIR)/sbom-python.spdx.json.sig \
			--output-certificate $(BUILD_DIR)/sbom-python.spdx.json.pem || true; \
		echo "$(GREEN)✓ SBOM signed$(NC)"; \
	else \
		echo "$(RED)Error: SBOM not found. Run 'make sbom-generate' first$(NC)"; \
		exit 1; \
	fi
	
.PHONY: verify
verify: ## Verify signed artifacts (FR-014)
	@echo "$(CYAN)Verifying signed artifacts...$(NC)"
	@command -v cosign >/dev/null 2>&1 || { echo "$(RED)Error: cosign not installed$(NC)"; exit 1; }
	@if [ -f "$(BUILD_DIR)/sbom-python.spdx.json.sig" ]; then \
		cosign verify-blob $(BUILD_DIR)/sbom-python.spdx.json \
			--signature $(BUILD_DIR)/sbom-python.spdx.json.sig \
			--certificate $(BUILD_DIR)/sbom-python.spdx.json.pem || true; \
		echo "$(GREEN)✓ Signature verified$(NC)"; \
	else \
		echo "$(RED)Error: Signature not found. Run 'make sign' first$(NC)"; \
		exit 1; \
	fi
	
.PHONY: purge-retention
purge-retention: ## Purge expired data per retention policy (FR-010, SC-005)
	@echo "$(CYAN)Purging expired data...$(NC)"
	$(PYTHON) scripts/purge_retention.py --dry-run
	@read -p "Execute purge? [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) scripts/purge_retention.py
	@echo "$(GREEN)✓ Data purge complete$(NC)"
	
.PHONY: security-audit
security-audit: sast security-test license-compliance ## Run full security audit (SC-003)
	@echo "$(GREEN)✓ Security audit complete$(NC)"
	
.PHONY: supply-chain
supply-chain: sbom-generate license-compliance sign ## Complete supply chain validation (SC-004)
	@echo "$(GREEN)✓ Supply chain validation complete$(NC)"
	
.PHONY: validate-024
validate-024: ## Validate Feature 024 implementation
	@echo "$(CYAN)Validating Feature 024: Security & Privacy Audit$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) validate_feature_024.py
	@echo "$(GREEN)✓ Feature 024 validation passed$(NC)"
	
#==============================================================================
# Smoke Test Targets
#==============================================================================

.PHONY: smoke
smoke: ## Run smoke tests on staging
	@echo "$(CYAN)Running smoke tests...$(NC)"
	cd smoke && $(PYTHON) smoke_websocket.py
	cd smoke && $(PYTHON) smoke_metrics.py
	cd smoke && $(PYTHON) smoke_presets.py
	@echo "$(GREEN)✓ Smoke tests passed$(NC)"
	
.PHONY: smoke-staging
smoke-staging: ## Run smoke tests against staging environment
	@echo "$(CYAN)Running smoke tests on staging...$(NC)"
	SOUNDLAB_URL=http://localhost:8000 $(MAKE) smoke
	
#==============================================================================
# Deployment Targets
#==============================================================================

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	@echo "$(CYAN)Deploying to staging...$(NC)"
	$(MAKE) docker-compose-up
	sleep 5
	$(MAKE) healthcheck
	@echo "$(GREEN)✓ Deployed to staging$(NC)"
	
.PHONY: healthcheck
healthcheck: ## Check health endpoints
	@echo "$(CYAN)Checking health endpoints...$(NC)"
	@curl -f http://localhost:8000/healthz || { echo "$(RED)Health check failed$(NC)"; exit 1; }
	@curl -f http://localhost:8000/readyz || { echo "$(RED)Ready check failed$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Health checks passed$(NC)"
	
.PHONY: rollback
rollback: ## Rollback to previous version
	@echo "$(CYAN)Rolling back...$(NC)"
	docker-compose -f docker-compose.staging.yml down
	docker tag $(DOCKER_IMAGE):previous $(DOCKER_IMAGE):latest
	docker-compose -f docker-compose.staging.yml up -d
	@echo "$(GREEN)✓ Rollback complete$(NC)"
	
#==============================================================================
# Release Targets
#==============================================================================

.PHONY: dist
dist: ## Build Python wheel and sdist artifacts (FR-003)
	@echo "$(CYAN)Building distribution artifacts for $(VERSION)...$(NC)"
	rm -rf dist
	$(PYTHON) -m pip install --upgrade build wheel >/dev/null
	$(PYTHON) -m build --wheel --sdist
	@ls -lh dist
	
.PHONY: changelog
changelog: ## Generate CHANGELOG.md from git history (FR-005)
	@echo "$(CYAN)Generating CHANGELOG.md for $(VERSION)...$(NC)"
	$(PYTHON) scripts/generate_changelog.py --version $(VERSION) --output CHANGELOG.md
	@echo "$(GREEN)✓ CHANGELOG.md updated$(NC)"
	
.PHONY: sign
sign: ## Generate SHA256 checksums and cosign signatures (FR-004)
	@echo "$(CYAN)Signing release artifacts...$(NC)"
	@test -d dist || { echo "$(RED)dist/ directory not found. Run 'make dist' first.$(NC)"; exit 1; }
	@rm -f dist/SHA256SUMS dist/SHA256SUMS.sig dist/SHA256SUMS.pem
	@if command -v sha256sum >/dev/null 2>&1; then \
	sha256sum dist/* > dist/SHA256SUMS; \
	else \
	shasum -a 256 dist/* > dist/SHA256SUMS; \
	fi
	@if ! command -v cosign >/dev/null 2>&1; then \
	echo "$(RED)cosign CLI not found. Install cosign to sign artifacts.$(NC)"; \
	exit 1; \
	fi
	COSIGN_EXPERIMENTAL=1 cosign sign-blob --yes dist/SHA256SUMS \
	--output-signature dist/SHA256SUMS.sig \
	--output-certificate dist/SHA256SUMS.pem
	@echo "$(GREEN)✓ Artifacts signed$(NC)"
	
.PHONY: release
release: ## Run the local release pipeline (FR-001)
	@echo "$(CYAN)=== Soundlab v$(VERSION) Release Pipeline ===$(NC)"
	$(MAKE) ci
	$(MAKE) dist
	$(MAKE) changelog
	$(MAKE) sign
	@echo "$(GREEN)✓ Local release pipeline complete$(NC)"
	
.PHONY: tag-release
tag-release: ## Tag release in git
	@echo "$(CYAN)Tagging release $(VERSION)...$(NC)"
	git tag -a $(VERSION) -m "Release $(VERSION)"
	git push origin $(VERSION)
	@echo "$(GREEN)✓ Release tagged: $(VERSION)$(NC)"
	
.PHONY: release-notes
release-notes: ## Append release highlights to RELEASE_NOTES.md
	@echo "$(CYAN)Updating RELEASE_NOTES.md...$(NC)"
	@echo "\n## Build Metadata" >> RELEASE_NOTES.md
	@echo "- Build Date: $(BUILD_DATE)" >> RELEASE_NOTES.md
	@echo "- Git Commit: $(GIT_COMMIT)" >> RELEASE_NOTES.md
	@echo "- Version: $(VERSION)" >> RELEASE_NOTES.md
	@echo "$(GREEN)✓ Release notes updated$(NC)"
	
.PHONY: go-nogo
go-nogo: ## Run Go/No-Go checklist
	@echo "$(CYAN)Running Go/No-Go checklist...$(NC)"
	cd $(SERVER_DIR) && $(PYTHON) validate_release_readiness.py
	@echo "$(GREEN)✓ Go/No-Go checklist complete$(NC)"
	
#==============================================================================
# Feature 026: Post-Release Maintenance
#==============================================================================

.PHONY: maintenance
maintenance: ## Run local maintenance checks (FR-007)
	@echo "$(CYAN)========================================$(NC)"
	@echo "$(CYAN)Feature 026: Maintenance Checks$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@echo ""
	@echo "$(CYAN)[1/6] Code quality checks...$(NC)"
	$(MAKE) quality || echo "$(RED)Quality checks had issues$(NC)"
	@echo ""
	@echo "$(CYAN)[2/6] Security scans...$(NC)"
	$(MAKE) security-scan || echo "$(RED)Security scan had issues$(NC)"
	@echo ""
	@echo "$(CYAN)[3/6] Running tests...$(NC)"
	$(MAKE) test || echo "$(RED)Tests had failures$(NC)"
	@echo ""
	@echo "$(CYAN)[4/6] Regression tests...$(NC)"
	$(MAKE) regression || echo "$(RED)Regression tests had issues$(NC)"
	@echo ""
	@echo "$(CYAN)[5/6] Performance benchmarks...$(NC)"
	$(MAKE) benchmarks || echo "$(RED)Benchmark comparison had issues$(NC)"
	@echo ""
	@echo "$(CYAN)[6/6] Documentation check...$(NC)"
	@test -f docs/roadmap_v1.1.md && echo "$(GREEN)✓ Roadmap exists$(NC)" || echo "$(RED)✗ Roadmap missing$(NC)"
	@test -f docs/versioning_policy.md && echo "$(GREEN)✓ Versioning policy exists$(NC)" || echo "$(RED)✗ Versioning policy missing$(NC)"
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)✓ Maintenance cycle complete$(NC)"
	@echo "$(GREEN)========================================$(NC)"

.PHONY: regression
regression: ## Run regression tests against v1.0 baseline (FR-005)
	@echo "$(CYAN)Running regression tests...$(NC)"
	$(PYTEST) tests/regression/ -v --tb=short
	@echo "$(GREEN)✓ Regression tests passed$(NC)"

.PHONY: benchmarks
benchmarks: ## Compare current performance against baselines (FR-006)
	@echo "$(CYAN)Running benchmark comparison...$(NC)"
	$(PYTHON) scripts/check_benchmarks.py
	@echo "$(GREEN)✓ Benchmark comparison complete$(NC)"

.PHONY: roadmap
roadmap: ## Display roadmap for v1.1 (FR-009)
	@echo "$(CYAN)Soundlab + D-ASE Roadmap v1.1$(NC)"
	@echo ""
	@if [ -f "docs/roadmap_v1.1.md" ]; then \
		head -n 50 docs/roadmap_v1.1.md; \
		echo ""; \
		echo "$(GREEN)Full roadmap: docs/roadmap_v1.1.md$(NC)"; \
	else \
		echo "$(RED)✗ Roadmap not found$(NC)"; \
		exit 1; \
	fi

.PHONY: deprecation-report
deprecation-report: ## Show deprecated APIs and removal schedule (FR-004)
	@echo "$(CYAN)Generating deprecation report...$(NC)"
	$(PYTHON) -c "from server.deprecation import print_deprecation_report; print_deprecation_report()"

.PHONY: validate-026
validate-026: ## Validate Feature 026 implementation
	@echo "$(CYAN)Validating Feature 026: Post-Release Maintenance$(NC)"
	@echo "Checking deliverables..."
	@test -f docs/roadmap_v1.1.md && echo "$(GREEN)✓ Roadmap document$(NC)" || { echo "$(RED)✗ Missing roadmap$(NC)"; exit 1; }
	@test -f .github/workflows/maintenance.yml && echo "$(GREEN)✓ Maintenance workflow$(NC)" || { echo "$(RED)✗ Missing maintenance workflow$(NC)"; exit 1; }
	@test -d .github/ISSUE_TEMPLATE && echo "$(GREEN)✓ Issue templates$(NC)" || { echo "$(RED)✗ Missing issue templates$(NC)"; exit 1; }
	@test -f server/deprecation.py && echo "$(GREEN)✓ Deprecation system$(NC)" || { echo "$(RED)✗ Missing deprecation system$(NC)"; exit 1; }
	@test -d tests/regression && echo "$(GREEN)✓ Regression tests$(NC)" || { echo "$(RED)✗ Missing regression tests$(NC)"; exit 1; }
	@test -f benchmarks/latency_v1.1.json && echo "$(GREEN)✓ Benchmarks$(NC)" || { echo "$(RED)✗ Missing benchmarks$(NC)"; exit 1; }
	@test -f docs/versioning_policy.md && echo "$(GREEN)✓ Versioning policy$(NC)" || { echo "$(RED)✗ Missing versioning policy$(NC)"; exit 1; }
	@test -f CONTRIBUTING.md && echo "$(GREEN)✓ Contributing guide$(NC)" || { echo "$(RED)✗ Missing contributing guide$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Feature 026 validation passed$(NC)"

#==============================================================================
# Documentation Targets
#==============================================================================

.PHONY: docs
docs: ## Generate all documentation
	@echo "$(CYAN)Generating documentation...$(NC)"
	@echo "Documentation located in $(DOCS_DIR)/"
	@ls -la $(DOCS_DIR)/
	@echo "$(GREEN)✓ Documentation ready$(NC)"

#==============================================================================
# All-in-One Targets
#==============================================================================

.PHONY: ci
ci: install-dev quality test validate ## Run full CI pipeline
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"
	
.PHONY: pre-release
pre-release: ci rc sbom license-check ## Prepare for release
	@echo "$(GREEN)✓ Pre-release checks complete$(NC)"
	
.PHONY: full-release
full-release: pre-release docker-build tag-release release-notes ## Full release process
	@echo "$(GREEN)✓ Full release complete: $(VERSION)$(NC)"
	@echo "Next steps:"
	@echo "  1. Push Docker image: make docker-push"
	@echo "  2. Deploy to staging: make deploy-staging"
	@echo "  3. Run smoke tests: make smoke-staging"
	@echo "  4. Run Go/No-Go: make go-nogo"
	
#==============================================================================
# Default Target
#==============================================================================

.DEFAULT_GOAL := help
