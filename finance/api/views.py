from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from prophet import Prophet
import io

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def forecast_financial_timeseries(request):
    """
    Prophet ile finansal zaman serisi tahmini yapar.
    Beklenen veri: {"dates": [...], "values": [...], "periods": 12}
    """
    try:
        dates = request.data.get('dates')
        values = request.data.get('values')
        periods = int(request.data.get('periods', 12))
        if not dates or not values or len(dates) != len(values):
            return Response({'error': 'Geçersiz veri.'}, status=status.HTTP_400_BAD_REQUEST)
        df = pd.DataFrame({'ds': pd.to_datetime(dates), 'y': values})
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=periods, freq='M')
        forecast = model.predict(future)
        result = {
            'forecast_dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'forecast_values': forecast['yhat'].round(2).tolist(),
        }
        return Response(result)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 