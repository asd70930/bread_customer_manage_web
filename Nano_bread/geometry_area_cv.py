import cv2
import numpy as np

# cv2.fillPoly(mask, [pts], (255), 8, 0)

class Fill_geometry:
    def __init__(self ,h ,w ,basis_points):
        ## 重點 1 : 減去偏移值(數字相加，但在圖像上是減少)
        self.bias_num = np.asarray([[1, 1], [0, 1], [0, 0], [1, 0]])
        self.mask = np.zeros((h, w), dtype=np.uint8)
        if len(basis_points) == 4 :
            cv2.fillPoly(self.mask, [np.asarray(basis_points) + self.bias_num], (255))
        else:
            # 會出現誤差，basis_points 所圍成面積不要太小，基本上不影響結果
            cv2.fillPoly(self.mask, [np.asarray(basis_points)], (255))


        self.mask_temp = self.mask.copy()
        self.init_points_num = self.compute_pints(self.mask_temp)
        # print("初始化 mask 255 個數 : " ,self.init_points_num)

    def obj_points_to_fill(self,obj_anchors):
        obj_anchors = np.asarray(obj_anchors) + self.bias_num
        cv2.fillPoly(self.mask_temp ,[obj_anchors] ,(0))
        # print("啟用填入後的數量  : " ,self.compute_pints(self.mask_temp))

    def imshow(self):
        cv2.imshow("frame" ,self.mask_temp)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
    def clear_mask(self):
        self.mask_temp = self.mask.copy()
        # print("clear_mask 數量後 : " ,self.compute_pints(self.mask_temp))

    def compute_pints(self ,mask_figure):
        return np.sum(mask_figure == 255)

    def area_ratio(self):
        return 100 - round( (self.compute_pints(self.mask_temp) / self.init_points_num) * 100 ,2)


if __name__ == "__main__":
    basis_points = [[182, 143], [402, 79], [432, 328], [107, 294]]
    obj_anchors1 = [[267 ,49] ,[480 ,49] ,[480 ,222] ,[267 ,222]]
    obj_anchors2 = [[293 ,164] ,[541 ,164] ,[541 ,384] ,[293 ,384]]
    total_anchors = [obj_anchors1 ,obj_anchors2]

    h ,w = 600 ,600
    model = Fill_geometry(h ,w ,basis_points)
    model.obj_points_to_fill(obj_anchors1)
    model.imshow()
    model.obj_points_to_fill(obj_anchors2)
    model.imshow()
    area_ratio = model.area_ratio()
    print("area_ratio : {}%".format(area_ratio))
    # 清除變回原基礎框
    model.clear_mask()

    print("--------- 測試組 2 ----------")

    basis_points1 = [[200 ,200] ,[300 ,200] ,[300 ,300] ,[200 ,300]]
    obj1 = [[225 ,100] ,[250 ,100] ,[250 ,400] ,[225 ,400]]
    obj2 = [[225 ,100] ,[275 ,100] ,[275 ,225] ,[225 ,225]]
    obj3 = [[275 ,275] ,[400 ,275] ,[400 ,400] ,[275 ,400]]
    total_obj_anchors = [obj1 ,obj2 ,obj3]

    h ,w = 600 ,600
    # [[+1 ,+1] ,[* ,+1] ,[* ,*] ,[+1 ,*]]
    model2 = Fill_geometry(h ,w ,basis_points1)



    for obj in total_obj_anchors:
        model2.obj_points_to_fill(obj)
        model2.imshow()




    area_ratio2 = model2.area_ratio()
    print("area_ratio : {}%".format(area_ratio2))

    print("--------- 測試 3 --------")
    ##  原本需減去偏移值(數字相加，但在圖像上是減少)，已經整合至 class 裡面
    basis_points2 = [[100 ,100] ,[110 ,100] ,[110 ,110] ,[100 ,110]]
    model3 = Fill_geometry(h ,w ,basis_points2)


    print("------- 測試 4 ----------")
    basis_points3 = [[439 ,233] ,[522 ,111] ,[606 ,233] ,[750 ,235] ,[679 ,358] ,[750 ,482] ,
                     [604 ,485] ,[522 ,605] ,[440 ,484] ,[293 ,483] ,[365 ,359] ,[294 ,233]]

    model4 = Fill_geometry(720 ,1280 ,basis_points3)
    model4.imshow()