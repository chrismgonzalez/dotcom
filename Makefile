BUCKET  := chrisdoescloud.com
STACK   := chrisdoescloud-site
REGION  := us-east-1

.PHONY: build deploy infra invalidate serve

build:
	uv run python build.py

serve: build
	uv run python -m http.server 8080 --directory dist

infra:
	sam deploy

deploy: build
	aws s3 sync dist/ s3://$(BUCKET) \
		--delete \
		--cache-control "public, max-age=31536000, immutable" \
		--exclude "*.html"
	aws s3 sync dist/ s3://$(BUCKET) \
		--delete \
		--cache-control "public, max-age=0, must-revalidate" \
		--exclude "*" \
		--include "*.html"
	$(MAKE) invalidate

invalidate:
	aws cloudfront create-invalidation \
		--distribution-id $$(aws cloudformation describe-stacks \
			--stack-name $(STACK) \
			--region $(REGION) \
			--query "Stacks[0].Outputs[?OutputKey=='DistributionId'].OutputValue" \
			--output text) \
		--paths "/*"
