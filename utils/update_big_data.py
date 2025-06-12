import requests
from models.statistik_satuan_pendidikan import StatistikSatuanPendidikan
from datetime import datetime, timezone

def update_big_data():
    url = "https://api.data.belajar.id/data-portal-backend/v1/master-data/satuan-pendidikan/statistics/360"
    response = requests.get(url)

    if response.status_code == 200:
        result = response.json()
        last_updated_str = result["meta"]["lastUpdatedAt"]
        last_updated_dt = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
        tahun = str(last_updated_dt.year)
        data = result["satuanPendidikanStatistics"]

        statistik = StatistikSatuanPendidikan.objects(year=tahun).first()

        if statistik:
            statistik.update(
                set__kbSederajat=data.get("kbSederajat", 0),
                set__tkSederajat=data.get("tkSederajat", 0),
                set__tpa=data.get("tpa", 0),
                set__sps=data.get("sps", 0),
                set__sdSederajat=data.get("sdSederajat", 0),
                set__smpSederajat=data.get("smpSederajat", 0),
                set__smaSederajat=data.get("smaSederajat", 0),
                set__smkSederajat=data.get("smkSederajat", 0),
                set__slb=data.get("slb", 0),
                set__dikmas=data.get("dikmas", 0),
                set__total=data.get("total", 0),
            )
            statistik.save()
        else:
            statistik = StatistikSatuanPendidikan(
                year=tahun,
                kbSederajat=data.get("kbSederajat", 0),
                tkSederajat=data.get("tkSederajat", 0),
                tpa=data.get("tpa", 0),
                sps=data.get("sps", 0),
                sdSederajat=data.get("sdSederajat", 0),
                smpSederajat=data.get("smpSederajat", 0),
                smaSederajat=data.get("smaSederajat", 0),
                smkSederajat=data.get("smkSederajat", 0),
                slb=data.get("slb", 0),
                dikmas=data.get("dikmas", 0),
                total=data.get("total", 0),
                created_at = datetime.now(timezone.utc),
                updated_at = datetime.now(timezone.utc)
            )
            statistik.save()

        print(f'Statistic updated successfully')
    else:
        print('Failed to update statistic')