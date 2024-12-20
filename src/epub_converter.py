import os
import subprocess
from pathlib import Path
from typing import List, Optional


class EpubConverter:
    def __init__(
        self,
        book_title: str,
        book_author: str,
        input_dir: str | Path,
        output_dir: str | Path,
        file_order: List[str],
        cover_image_path: Optional[str | Path] = None,
    ):
        self.book_title = book_title
        self.book_author = book_author
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.file_order = file_order
        self.cover_image = Path(cover_image_path).resolve() if cover_image_path else None
        self.output_file = f"{book_title}.epub"

    def validate_files(self) -> List[str]:
        """检查所有必需文件是否存在，返回缺失的文件列表"""
        missing_files = []
        for file in self.file_order:
            file_path = self.input_dir / file
            print(f"Checking file: {file_path}")
            if not file_path.exists():
                print(f"Warning: file {file_path} does not exist")
                missing_files.append(file)
            else:
                print(f"Found file: {file_path}")
        return missing_files

    def build_pandoc_command(self) -> List[str]:
        """构建pandoc命令"""
        input_files = [str(self.input_dir / filename) for filename in self.file_order]

        command = [
            "pandoc",
            "--from=markdown",
            "--to=epub",
            "-o",
            self.output_file,
            "--toc",
            "--toc-depth=2",
            "--epub-chapter-level=2",
            "--metadata",
            f"title={self.book_title}",
            "--metadata",
            f"author={self.book_author}",
        ]

        if self.cover_image and self.cover_image.exists():
            command.extend(["--epub-cover-image", str(self.cover_image)])
        else:
            print(f"Warning: Cover image {self.cover_image} does not exist")

        command.extend(input_files)
        return command

    def create_epub(self) -> bool:
        """
        创建EPUB文件
        返回：转换是否成功
        """
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 验证文件
        missing_files = self.validate_files()
        if missing_files:
            print(f"The following files are missing: {missing_files}")
            return False

        # 构建并执行命令
        command = self.build_pandoc_command()
        print("Executing command:")
        print(" ".join(command))

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Pandoc stdout:", result.stdout)
            print("Pandoc stderr:", result.stderr)

            # 移动文件到输出目录
            output_path = self.output_dir / self.output_file
            if output_path.exists():
                output_path.unlink()
            Path(self.output_file).rename(output_path)

            print(f"Successfully created EPUB file: {output_path}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")
            return False
        except Exception as e:
            print(f"Unknown error occurred: {e}")
            return False
