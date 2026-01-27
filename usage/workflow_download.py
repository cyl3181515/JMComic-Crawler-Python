from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
1252402
1252401
1252084
1252085
1252086
1251655
1251654
1251347
1251345
1251344
1251097
1251096
1136244
1250585
1250836
1250835
1250596
1250598
1249744
1249742
1249146
1249145
1248898
1248897
1249138
1248538
1248484
1248291
1248287
1247860
1247859
1247505
1143285
1247258
1247256
1246978
1246977
1246840
1246556
1246555
1246213
1246203
1245765
1245830
1245039
1245616
1245446
1244907
1244464
1244463
1244110
1243744
1244003
1248243
1243766
1243085
1243086
1241708
1241299
1241292
1241286
1227500
1241105
1241104
1241103
1241106
1240687
1240677
1240676
1240321
1240318
1240317
1240367
1239705
1239698
1239695
1239693
1239407
1239406
1239405
1239404
1239349
1239231
1239230
1238924
1238909
1238904
1238628
1238617
1238615
1238614
1238321
1238320
1238319
1238080
1238085
1238077
1238040
1237896
1237780
1237762
1237755
1237442
1237527
1237526
1237525
1237250
1237249
1237049
1237035
1237013
1236801
1236800
1236798
1236628
1236627
1236625
1236351
1236341
1236340
1236017
1236016
1235829
1235822
1235821
1235581
1235580
1235579
1235388
1235387
1235208
1235207
1234989
1234969
1234968
1234335
1234334
1234297
1233904
1233767
1233766
1233765
1233703
1233650
1233648
1233447
1233436
1232875
1232863
1232835
1232702
1232692
1232687
1232428
1232420
1203266
1232222
1232234
1232229
1232035
1232034
1232033
1231669
1231667
1231534
1231530
1230972
1230967
1230962
1230550
1230545
1230544
1230347
1230341
1230351
1230228
1230223
1230215
1230075
1230074
1227532
1229939
1229938
1229695
1229687
1199545
1229550
1229542
1229540
1229437
1229433
1229233
1229229
1228925
1228924
1228923
1228833
1228832
1228649
1228650
1228651
1228419
1228416
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
