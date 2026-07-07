from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
1445499
1444544
1444049
1442934
1442273
1439794
1438691
1437909
1435728
1433587
1430333
1429450
1428159
1426236
1422694
1421773
1410475
1386504
1371700
1292078
1292074
1257854
1257223
1256742
1255655
1254973
1253678
1250348
1246198
123927
1237884
1237883
1236793
1236408
1234343
1233499
1231592
1229104
1226548
1215085
1213183
1207964
1203553
1202604
1201036
1201032
1198346
1193938
1192929
1189650
1188788
1182993
1182984
1182983
1176888
1174459
1173677
1169679
1168965
1168964
1165040
1162594
1160191
1158361
1158357
1158161
1152984
1152982
1152981
1152945
1152145
1149063
1142128
1141306
1133120
1129834
1128716
1125606
1125310
1100966
1076141
183092
1120072
1115975
1113856
1112278
1107430
1104351
1097335
1094997
1091272
1090197
1090194
1085900
1085769
1084413
1080609
1079732
1079387
1076883
1075785
1075206
1072265
1071939
1071320
1063145
1062577
1062571
1062110
1054176
1054172
1053385
1052034
1051224
1047110
1047100
1044048
1042357
1041867
1040803
1038767
1038510
1037713
1034420
1033440
1033181
1030112
1029514
1028368
1028153
1025558
1025545
1025543
1025317
1023165
1023164
1022658
1022259
1021771
1020306
1020305
1019816
1015385
1015383
1014656
1014655
650124
649704
649662
649532
643932
643919
642196
642193
641300
641299
641298
639937
639407
636711
636127
635890
1448026
1237909
1237970
1221350
1132111
1035849
1019844
622721
568433
564537
364315
333104
325913
231791
230707
200258
149238
145909
123003
119551
76142
76141
72502
66802
63097
63078
61558
61546
61093
43626
43578
27176
23313
18750
17111
14564
1448054
1442438
1432968
1423854
1254403
1230631
1218934
1168908
1114797
1114796
1059005
605870
602564
602517
599349
598997
571343
554799
503861
494349
418605
375587
353632
209342
209341
208514
139074
103738
59751
52267
38272
24512
1452173
1445547
1437951
1435767
1369311
1369313
1239396
1231905
1229921
1222498
1217545
1134567
1134563
1013357
644971
594876
533192
511852
509651
483372
433246
428390
420261
417930
384795
384794
380101
37077
320508
31839
306311
30664
302397
299027
278453
273695
267563
264596
258851
23598
229545
205747
148777
124727
112867
105711
97186
58523
49921
41050
1449279
1318547
1205544
1205513
1142100
1142099
1140923
602537
602506
600118
599908
599470
599467
591440
575308
575307
575167
574924
147350
122963
95105
61267
57899
55496
49353
11031
9805
9072
8752
1127162
1439603
1432634
1193820
1164867
1156507
1079517
1037271
651699
633506
551870
486175
462486
424436
398019
351157
344537
308794
228505
215804
208843
206024
178996
148165
389788
1440995
1440994
1440993
1436657
1430770
1430759
1430630
1430488
1430334
1426219
1415637
1286119
1286110
1286076
1264337
1251645
1243914
1246527
1239606
1239607
1239605
1236401
1231726
1231714
1228464
1222428
1215828
1207840
1207839
1207838
1199606
1191858
1189289
1189288
1189287
1189002
1176008
1170795
1168483
1168482
1168481
1137735
1133153
1133155
1133154
1129236
1120045
1119697
1113272
1113271
1113270
1084405
1084402
1084400
1069025
1042328
1042171
1034636
1130634
1096896
644615
641833
630637
630636
630634
627135
593571
590259
590248
640392
639553
617848
45215
612818
583874
576245
574022
573911
572799
569472
566856
566848
566577
560566
557368
557369
550881
547787
547786
'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)

    pdf_option = env('PDF_OPTION', None)
    if pdf_option and pdf_option != '否':
        call_when = 'after_album' if pdf_option == '是 | 本子维度合并pdf' else 'after_photo'
        
        pdf_name_rule = env('PDF_NAME_RULE', None)
        if isinstance(pdf_name_rule, str):
            pdf_name_rule = pdf_name_rule.strip()
            
        if not pdf_name_rule:
            pdf_name_rule = '[JM{Aid}] {Atitle}' if call_when == 'after_album' else '[JM{Aid}] 第{Pindex}章-JM{Pid}-{Ptitle}'
            
        plugin = [{
            'plugin': Img2pdfPlugin.plugin_key,
            'kwargs': {
                'pdf_dir': option.dir_rule.base_dir + '/pdf/',
                'filename_rule': pdf_name_rule,
                'delete_original_file': True,
            }
        }]
        option.plugins[call_when] = plugin


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)

        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url

        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )

        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
        异常监听器，实现了在 GitHub Actions 下，把请求错误的信息下载到文件，方便调试和通知使用者
        """
        # 决定要写入的文件路径
        path = decide_filepath(e)

        # 准备内容
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'响应文本: {resp.text}')

        # 写文件
        write_text(path, '\n'.join(content))

    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()
