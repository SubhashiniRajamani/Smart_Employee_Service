from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

old = '''  FrontendBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub smart-employee-frontend-${AWS::AccountId}-${Environment}
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: index.html
'''

new = '''  FrontendBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub smart-employee-frontend-${AWS::AccountId}-${Environment}

      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        IgnorePublicAcls: false
        BlockPublicPolicy: false
        RestrictPublicBuckets: false

      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: index.html
'''

if old not in text:
    raise SystemExit("ERROR: Could not find FrontendBucket block")

text = text.replace(old, new, 1)

path.write_text(text)

print("Updated FrontendBucket public access configuration.")
