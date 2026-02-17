from PIL import Image, ImageDraw, ImageFont

# 打开截图
img = Image.open('xiaohongshu-xy.png')
draw = ImageDraw.Draw(img)

# 坐标信息
input_center_x, input_center_y = 1520, 469
input_x, input_y = 1392, 445
input_w, input_h = 256, 48

# 按钮大概位置 (根据用户之前的标注)
btn_x, btn_y = 960, 470

# 绘制输入框矩形 (蓝色)
draw.rectangle(
    [input_x, input_y, input_x + input_w, input_y + input_h],
    outline='blue', width=3
)

# 绘制中心点 (红点)
draw.ellipse(
    [input_center_x - 5, input_center_y - 5, 
     input_center_x + 5, input_center_y + 5],
    fill='red', outline='red'
)

# 绘制按钮位置 (绿色)
draw.rectangle(
    [btn_x - 60, btn_y - 20, btn_x + 60, btn_y + 20],
    outline='green', width=3
)

# 添加文字标注
draw.text((input_x, input_y - 25), '输入框 (手机号)', fill='blue')
draw.text((btn_x - 80, btn_y - 35), '按钮位置?', fill='green')
draw.text((btn_x - 30, btn_y + 25), f'({btn_x}, {btn_y})', fill='green')

# 保存
img.save('xiaohongshu-marked.png')
print('✅ 已绘制坐标标记')
print('文件: xiaohongshu-marked.png')
