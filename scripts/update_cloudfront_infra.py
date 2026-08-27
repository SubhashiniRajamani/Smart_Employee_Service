from pathlib import Path

path = Path("infrastructure/main.yaml")
text = path.read_text()

if "\nOutputs:" not in text:
    raise SystemExit("ERROR: Outputs section not found")

block = r'''
  FrontendCloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Enabled: true
        DefaultRootObject: index.html

        Origins:
          - Id: FrontendS3WebsiteOrigin
            DomainName: !Sub ${FrontendBucket}.s3-website.${AWS::Region}.amazonaws.com
            CustomOriginConfig:
              HTTPPort: 80
              HTTPSPort: 443
              OriginProtocolPolicy: http-only

        DefaultCacheBehavior:
          TargetOriginId: FrontendS3WebsiteOrigin
          ViewerProtocolPolicy: redirect-to-https
          AllowedMethods:
            - GET
            - HEAD
          CachedMethods:
            - GET
            - HEAD
          ForwardedValues:
            QueryString: false
            Cookies:
              Forward: none

        CustomErrorResponses:
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html

          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /index.html

        ViewerCertificate:
          CloudFrontDefaultCertificate: true
'''

output_block = r'''
  FrontendCloudFrontUrl:
    Description: CloudFront HTTPS frontend URL
    Value: !Sub https://${FrontendCloudFrontDistribution.DomainName}
'''

if "FrontendCloudFrontDistribution:" not in text:
    pos = text.index("\nOutputs:")
    text = text[:pos] + "\n" + block + "\n" + text[pos:]
    print("Added CloudFront distribution.")
else:
    print("CloudFront distribution already exists.")

if "FrontendCloudFrontUrl:" not in text:
    text = text.rstrip() + "\n\n" + output_block + "\n"
    print("Added CloudFront output.")
else:
    print("CloudFront output already exists.")

path.write_text(text)
