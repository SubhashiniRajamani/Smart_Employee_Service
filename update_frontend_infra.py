from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

if "\nOutputs:" not in text:
    raise SystemExit("ERROR: Outputs section not found")

block = r'''
  FrontendBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub smart-employee-frontend-${AWS::AccountId}-${Environment}
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: index.html

  FrontendBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref FrontendBucket
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Sid: PublicReadForWebsite
            Effect: Allow
            Principal: "*"
            Action:
              - s3:GetObject
            Resource: !Sub ${FrontendBucket.Arn}/*
'''

if "FrontendBucket:" in text:
    print("Frontend bucket resources already exist.")
else:
    pos = text.index("\nOutputs:")
    text = text[:pos] + "\n" + block + "\n" + text[pos:]
    path.write_text(text)
    print("Added frontend S3 resources.")
