import pathlib
import pprint
import re
import shutil

import frontmatter
import mistletoe

from generator import const
from generator import utils
from tqdm import tqdm


# TODO: リセット処理をする関数を書く


class FrontMatterError(Exception):
    """Front Matterに異常がある事を知らせるクラス"""

    print("Front Matterの値が異常です！")


class FileNameExtensionError(Exception):
    """ファイルが非対応の形式である事を知らせるクラス"""

    print("ファイルが対応していない形式です！")


class HtmlObject:
    """レンダリングされたHTMLなどのメタ情報をまとめたクラスです
    filename: レンダリングするファイル名 String
    """

    def __init__(self, filetuple):
        """クラス変数を初期化するコンストラクタ
        filename: ファイル名

        get_rendered_text()
        レンダリングしたテキストを返す
        引数なし
        戻り値: レンダリング後の文字列

        """
        self.filename = const.MARKDOWN_DIR / filetuple[0].with_suffix(
            "." + filetuple[1]
        )
        target = self.filename
        print(target)

        with open(target) as file:
            # TODO: lineをリスト形式に変更しておく
            self.metadeta, self.content = frontmatter.parse(file.read())
            if type(self.metadeta) == type(dict()):
                print("Type Check [[ OK ]]")

        file_extention = filetuple[1]
        print("File Extention ==> " + str(file_extention))
        if file_extention == "md":
            self.mkup = mistletoe.markdown(self.content)

        elif file_extention == "html":
            self.mkup = self.content

        else:
            print("レンダリングに対応しているファイル形式はMarkDown形式かHTMLです。")

            raise FileNameExtensionError()

    def get_rendered_text(self):
        """レンダリングしたテキストを返す
        引数なし
        戻り値: レンダリング後の文字列
        """
        try:
            self.is_publish = self.metadeta["publish"]

        except KeyError:
            print(
                """Front Matterのpublishが指定されていません！publishは必須の値です。publishは設定されていますか？
                    設定例:(Trueで公開、Falseで非公開)
                        ---
                        publish: True
                        ---"""
            )
            raise FrontMatterError

        return self.mkup

    def get_metadeta(self):
        """ファイルのメタデータを取得する"""

        if len(self.metadeta) == 0:
            raise FrontMatterError

        return self.metadeta


def get_dir_list(dir_name):
    """ディレクトリ構造を取得する
    dir_name: ターゲットになるディレクトリ。contents/markdownディレクトリ配下にある必要がある

    戻り値:
        ディレクトリ、ファイルパス(pathlib.Pathオブジェクト)と拡張子が分離したタプルのタプル
        >>>dirs, files = get_dir_list("demo")
        >>>print(dirs)
        >>>print(files)
        >>>('demo/memos', 'demo/contents')
        [(PosixPath('demo/index'), 'md'), (PosixPath('demo/memos/memo'), 'md'), (PosixPath('demo/contents/sample'), 'md'), (PosixPath('demo/contents/greeting'), 'md')]
    """
    dir_list = list()
    file_list = list()

    print(const.MARKDOWN_DIR)
    path_obj = const.MARKDOWN_DIR / pathlib.Path(dir_name)
    print("path_obj ==> " + str(path_obj))
    targets = path_obj.glob("**/*")

    print("Search target...")
    for target in tqdm(targets):
        print("i ==> " + str(target))
        if target.is_file():
            file_list.append(
                pathlib.Path(re.sub("\.\.\/contents\/markdowns\/", "", str(target)))
            )
        else:
            dir_list.append(
                pathlib.Path(re.sub("\.\.\/contents\/markdowns\/", "", str(target)))
            )
    path_and_name = list()
    print(dir_list)

    print("Set Filelist...")
    for i in tqdm(file_list):
        obj = pathlib.Path(i)
        path_and_name.append((obj.parent / obj.stem, obj.suffix[1:]))

    return (tuple(dir_list), path_and_name)


def make_dir(dirs, exist=True):
    """ディレクトリ構造を再構築する
    dirs: ディレクトリパスのリスト。pathlib.Pathのインスタンスである必要がある。
    exist: すでにディレクトリがある場合でもエラーを出さずにディレクトリを作成する。

    戻り値はない。
    """
    # ディレクトリ作成
    print("Make Directory...")
    for path in tqdm(dirs):
        target = const.OUTPUT_DIR / path
        print("make dir ==> " + str(target))
        target.mkdir(parents=True, exist_ok=exist)


def make_filepath(file_path, suf="html"):
    """出力先のファイルパスを生成する
    files: ファイルパスのリスト。各要素はpathlib.Pathのインスタンス。
    suf: 変更先の拡張子の文字列。デフォルトは"html"

    戻り値:
        拡張子を変更したファイルのパス
    """

    path = const.OUTPUT_DIR / file_path
    result = path.with_suffix("." + suf)
    # print(elem[0])
    # print(path.with_suffix("." + suf))
    return result


def writer(output_path, text):
    """ファイル書き込みを行う
    output_path: 書き込み先のファイルパス
    text: 書き込む内容
    """
    # TODO: 書き込み処理の有効化
    print("write ==> " + str(output_path))
    with open(output_path, mode="w") as f:
        f.write(text)

def all_clean():
    """outputディレクトリを全削除する"""
    ans = input("レンダリング済みファイルを全削除します。よろしいですか？ y/N ")
    if ans == "y":
        shutil.rmtree(const.OUTPUT_DIR)
        const.OUTPUT_DIR.mkdir()

    else:
        return


def main(target):
    dirs, files = get_dir_list(target)
    make_dir(dirs)
    print ("Run the process...")
    for file in tqdm(files):
        print("Target File Path ==> " + str(const.MARKDOWN_DIR / file[0].with_suffix("." + file[1])))
        # 取得したファイルパスからHtmlObujectインスタンスを作成する
        html_obj = HtmlObject(file)
        # レンダリング結果の書き込み
        writer(make_filepath(file[0]), html_obj.get_rendered_text())


# all_clean()
main("demo")
