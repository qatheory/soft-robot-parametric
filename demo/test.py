danh_sach_dong = [10, 20]


def them_phan_tu_vao_mang(ten_mang, gia_tri, vi_tri):
    ten_mang.insert(vi_tri, gia_tri)


them_phan_tu_vao_mang(danh_sach_dong, 5, 1)
print(danh_sach_dong)
