from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
1246198
1100966
1237884
1237883
1236793
1236408
1234343
1233499
1229104
1231592
1226548
1215085
1213183
1211168
1207964
1203553
1202604
1201036
1201032
1198346
1193938
1192929
1182984
1189650
1168965
1162594
1076141
1188788
1182993
1174459
1182983
1176888
1173677
1169679
1168964
1160191
1165040
1158361
1158161
1152945
1158357
1152984
1152982
1152981
1152145
1149063
1142128
1141306
1133120
1129834
1128716
1125606
1125310
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
1014656
650124
639407
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
1014655
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
636711
636127
635890
632541
632091
631044
631038
627978
614677
613012
613008
612863
612857
612856
612855
612854
612853
612852
612851
612850
612849
612848
612847
612730
605689
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
