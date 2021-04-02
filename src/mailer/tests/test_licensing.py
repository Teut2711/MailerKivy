from mailer.main import  is_license_valid, LicenseModalView
import datetime
import requests
import pytest



decrypted_data = decode_data(encrypted_data={
    "license_key":"dsGX5mHbEJzjObh9ctjftsv9iXxYCUj7mLpZnua0J7M=",
    "token":"gAAAAABgafOVFecVKUnAVFy5_L0y0lprKLsaD29mVY_g2K9nG6hf1bxzHYNsrKrT64lir9hjuuL2CR2qUnk61DXhtGRXWINfCFELOPVmPWSobbjTb9YbWk7xYnS7wrVra_OrgPUh5NZwOGyZvFEnZx34Rq9oH2WZI0C_c8lutuvqeuolHa5xFbV6SNxSmYy8pj0ky673KKIyp5KuxpYuBk6DAO2bm4B1g0Ck4OPa03LQcMjt4ssE3oa_q2foDb-D9_Ji1-E1HPmOA4yIDR8KhWtIz3UDxRSlUIkDTuUNhH75fy8EaedXqBPegpI21k8k9V-0QwiR8BVz-ogIQ_pIDuqkvRmVoTYWX1PHkMPhSzapCjL205AEiYOE5lS5Golqu3JVYLYkBAphMRQUYOGOyysSE4ySvPwhc4lktZQ5zs8Eq8E2H_S8P-JTFctD_CUNkuetKiU3lydO"
})

def test_decode_data():
    
    assert decrypted_data == {
        "license_key":"dsGX5mHbEJzjObh9ctjftsv9iXxYCUj7mLpZnua0J7M=",
       "system_id":"4C4C4544-004A-3010-8039-C6C04F4A3232",
      "registration_start_time":datetime.datetime(year=2021, month=4,hour=0, day=3  ).isoformat()+"+05:30",
      "registration_end_time":datetime.datetime(year=2021, month=4,hour=0, day=6  ).isoformat()+"+05:30",        
  "validity_period":
      {"years":1,
      "months":0
}
   }

def test_is_license_valid():

    def test_LicenseModelView():
        l = LicenseModalView()


        return l._get_new_token(decrypted_data, current_time)   
        
    token = test_LicenseModelView()   
    boolean, _ = is_license_valid(decrypted_data=decode_data({"license_key":decrypted_data["license_key"], "token":token}))
    assert boolean == True
   
   
   