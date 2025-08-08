# Manual Deployment Guide

## Prerequisites

1. AWS CLI configured with appropriate permissions
2. Supabase PostgreSQL database setup
3. Database tables created (see README.md)

## Step-by-Step Deployment

### 1. Setup S3 Deployment Bucket
```bash
./setup-s3.sh score-handler-deployment-bucket us-east-1
```

### 2. Set Doppler Secrets

Set your secrets in Doppler:

```bash
doppler secrets set DATABASE_URL="postgresql://postgres.khewnzogdzolwyflgazn:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
doppler secrets set API_KEY="your-api-key"
```

### 3. Deploy Lambda Function
```bash
./deploy.sh dev score-handler-deployment-bucket YOUR_DOPPLER_TOKEN
```

### 4. Test Deployment

Test the health endpoint:
```bash
curl https://YOUR_API_GATEWAY_URL/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "score-handler"
}
```

## Security Best Practices

### Database Password Security
- ✅ **DO**: Use Doppler for secret management
- ✅ **DO**: Rotate passwords regularly
- ❌ **DON'T**: Hardcode passwords in code
- ❌ **DON'T**: Put passwords in environment variables

### SSL Configuration
- ✅ **DO**: Always use `sslmode=require`
- ✅ **DO**: Use Supabase's pooler (port 6543)
- ✅ **DO**: Verify SSL certificates

### Connection String Format
```
postgresql://postgres.khewnzogdzolwyflgazn:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

## Troubleshooting

### Common Issues

1. **Doppler token invalid**
   - Verify token is correct: `doppler secrets --token YOUR_TOKEN`
   - Check project and config are correct

2. **Database connection failed**
   - Verify Supabase connection string
   - Check SSL configuration
   - Ensure tables exist

3. **Lambda timeout**
   - Check CloudWatch logs
   - Verify database connectivity
   - Consider increasing timeout

### Logs
View Lambda logs:
```bash
aws logs tail /aws/lambda/score-handler-dev --follow
```

## Environment Variables

The Lambda function uses these environment variables (set via CloudFormation):

- `DATABASE_URL`: Retrieved from Doppler
- `SECRET_KEY`: Retrieved from Doppler
- `DOPPLER_TOKEN`: Doppler service token  
- `ENVIRONMENT`: Deployment environment (dev/staging/prod)

## API Testing

### Register Survey
```bash
curl -X POST https://YOUR_API_URL/survey \
  -H "Content-Type: application/json" \
  -d '{
    "demographics": {
      "idNumber": "12345678",
      "gender": "F",
      "occupation": "Engineer"
    },
    "sections": {
      "financialResponsibility": {"data": {"q1": 4, "q2": 5}, "weight": 0.8},
      "riskAversion": {"data": {"q1": 3, "q2": 4}, "weight": 0.7}
    }
  }'
```

### Generate Repayment Plan
```bash
curl -X POST https://YOUR_API_URL/repayment-plan \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "12345678",
    "payment_type": "period",
    "period": 12,
    "amount": 10000
  }'
```

### Get User Amortization
```bash
curl https://YOUR_API_URL/repayment-plan/12345678
```