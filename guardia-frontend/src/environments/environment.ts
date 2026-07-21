export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  awsApiUrl: 'http://localhost:8007/api/v1',
  // IGA Thresholds (espelhar os valores do backend/app/config.py)
  iraThresholds: {
    moderate: 40.0,
    critical: 70.0,
  },
};
