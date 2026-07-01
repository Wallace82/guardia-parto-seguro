import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.s3_service import s3_service
from app.schemas.s3 import S3BucketType
from botocore.exceptions import ClientError

@pytest.mark.asyncio
async def test_generate_presigned_url_success(mock_aioboto3_session):
    client_mock = AsyncMock()
    mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
    client_mock.generate_presigned_url.return_value = "https://s3.amazonaws.com/media/file.mp4"

    url = await s3_service.generate_presigned_url(
        client_method='put_object',
        file_name='file.mp4',
        bucket_type=S3BucketType.media,
        expiration=3600,
        content_type='video/mp4'
    )

    assert url == "https://s3.amazonaws.com/media/file.mp4"
    mock_aioboto3_session.client.assert_called_once_with('s3', region_name='us-east-1')
    client_mock.generate_presigned_url.assert_called_once_with(
        ClientMethod='put_object',
        Params={
            'Bucket': 'guardia-parto-seguro-media-dev-foton',
            'Key': 'file.mp4',
            'ContentType': 'video/mp4'
        },
        ExpiresIn=3600
    )

@pytest.mark.asyncio
async def test_generate_presigned_url_reports(mock_aioboto3_session):
    client_mock = AsyncMock()
    mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
    client_mock.generate_presigned_url.return_value = "https://s3.amazonaws.com/reports/file.pdf"

    url = await s3_service.generate_presigned_url(
        client_method='get_object',
        file_name='file.pdf',
        bucket_type=S3BucketType.reports,
        expiration=1800
    )

    assert url == "https://s3.amazonaws.com/reports/file.pdf"
    client_mock.generate_presigned_url.assert_called_once_with(
        ClientMethod='get_object',
        Params={
            'Bucket': 'guardia-parto-seguro-reports-dev-foton',
            'Key': 'file.pdf'
        },
        ExpiresIn=1800
    )

@pytest.mark.asyncio
async def test_generate_presigned_url_error(mock_aioboto3_session):
    client_mock = AsyncMock()
    mock_aioboto3_session.client.return_value.__aenter__.return_value = client_mock
    
    error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}}
    client_mock.generate_presigned_url.side_effect = ClientError(error_response, 'generate_presigned_url')

    with pytest.raises(ClientError):
        await s3_service.generate_presigned_url(
            client_method='put_object',
            file_name='file.mp4',
            bucket_type=S3BucketType.media
        )
