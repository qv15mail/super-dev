# -*- coding: utf-8 -*-
"""
数据库迁移生成器 - 生成数据库迁移脚本

开发：Excellent（11964948@qq.com）
功能：基于 Spec 规范生成数据库迁移脚本
作用：自动化数据库版本管理
创建时间：2025-12-30
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import datetime


class DatabaseType(Enum):
    """数据库类型"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    SQLITE = "sqlite"


class ORMType(Enum):
    """ORM 框架类型"""
    PRISMA = "prisma"
    TYPEORM = "typeorm"
    SEQUELIZE = "sequelize"
    SQLALCHEMY = "sqlalchemy"
    DJANGO = "django"
    MONGOOSE = "mongoose"


@dataclass
class Column:
    """数据库列定义"""
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None
    foreign_key: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class Table:
    """数据库表定义"""
    name: str
    columns: list[Column]
    indexes: list[str] = None
    comment: Optional[str] = None

    def __post_init__(self):
        if self.indexes is None:
            self.indexes = []


class MigrationGenerator:
    """数据库迁移生成器"""

    def __init__(
        self,
        project_dir: Path,
        name: str,
        tech_stack: dict,
        db_type: DatabaseType = DatabaseType.POSTGRESQL,
        orm_type: Optional[ORMType] = None
    ):
        self.project_dir = Path(project_dir).resolve()
        self.name = name
        self.tech_stack = tech_stack
        self.backend = tech_stack.get("backend", "node")

        # 自动推断 ORM 类型
        if orm_type is None:
            orm_type = self._infer_orm_type()
        self.orm_type = orm_type
        self.db_type = db_type

        # 读取 Spec 规范
        self.entities = self._load_entities()

    def generate(self) -> dict[str, str]:
        """生成迁移脚本"""
        if self.orm_type == ORMType.PRISMA:
            return self._generate_prisma_migration()
        elif self.orm_type == ORMType.TYPEORM:
            return self._generate_typeorm_migration()
        elif self.orm_type == ORMType.SQLALCHEMY:
            return self._generate_sqlalchemy_migration()
        elif self.orm_type == ORMType.DJANGO:
            return self._generate_django_migration()
        elif self.orm_type == ORMType.SEQUELIZE:
            return self._generate_sequelize_migration()
        elif self.orm_type == ORMType.MONGOOSE:
            return self._generate_mongoose_migration()
        else:
            return self._generate_sql_migration()

    def _infer_orm_type(self) -> ORMType:
        """推断 ORM 类型"""
        backend = self.backend.lower()

        if backend == "node":
            # 检查 package.json
            package_json = self.project_dir / "package.json"
            if package_json.exists():
                content = package_json.read_text(encoding='utf-8')
                if "prisma" in content:
                    return ORMType.PRISMA
                elif "typeorm" in content:
                    return ORMType.TYPEORM
                elif "sequelize" in content:
                    return ORMType.SEQUELIZE
            # 默认使用 Prisma
            return ORMType.PRISMA

        elif backend == "python":
            # 检查 requirements.txt 或 pyproject.toml
            for file_name in ["requirements.txt", "pyproject.toml"]:
                req_file = self.project_dir / file_name
                if req_file.exists():
                    content = req_file.read_text(encoding='utf-8')
                    if "sqlalchemy" in content:
                        return ORMType.SQLALCHEMY
                    elif "django" in content:
                        return ORMType.DJANGO
            # 默认使用 SQLAlchemy
            return ORMType.SQLALCHEMY

        # 默认返回 SQL
        return ORMType.PRISMA

    def _load_entities(self) -> list[Table]:
        """从 Spec 规范加载实体定义"""
        entities = []

        # 尝试从 Spec 文件读取
        spec_dir = self.project_dir / ".super-dev" / "specs"
        if spec_dir.exists():
            for spec_file in spec_dir.glob("*.md"):
                content = spec_file.read_text(encoding='utf-8')
                entities.extend(self._parse_entities_from_spec(content))

        # 如果没有找到实体，生成默认的
        if not entities:
            entities = self._generate_default_entities()

        return entities

    def _parse_entities_from_spec(self, content: str) -> list[Table]:
        """从 Spec 内容解析实体定义"""
        entities = []

        # 简单解析：查找 ## Entity 或 ### Entity 标题
        lines = content.split("\n")
        current_entity = None
        current_columns = []

        for line in lines:
            if line.startswith("### ") and "Table" in line:
                # 新实体
                if current_entity and current_columns:
                    entities.append(Table(current_entity, current_columns))

                # 提取表名
                table_name = line.replace("###", "").strip().split()[0].lower()
                current_entity = table_name
                current_columns = []

            elif current_entity and line.strip().startswith("-"):
                # 解析列定义
                col_def = line.strip()[1:].strip()
                current_columns.append(self._parse_column(col_def))

        # 添加最后一个实体
        if current_entity and current_columns:
            entities.append(Table(current_entity, current_columns))

        return entities

    def _parse_column(self, col_def: str) -> Column:
        """解析列定义"""
        # 简单解析，实际应该更复杂
        parts = col_def.split(":")
        if len(parts) >= 2:
            name = parts[0].strip()
            col_type = parts[1].strip()
        else:
            name = col_def
            col_type = "string"

        return Column(
            name=name,
            type=col_type,
            nullable="primary" not in col_def.lower(),
            primary_key="primary" in col_def.lower()
        )

    def _generate_default_entities(self) -> list[Table]:
        """生成默认实体"""
        return [
            Table(
                name="users",
                columns=[
                    Column("id", "uuid", primary_key=True, comment="用户 ID"),
                    Column("email", "varchar(255)", unique=True, comment="邮箱"),
                    Column("password_hash", "varchar(255)", comment="密码哈希"),
                    Column("name", "varchar(100)", comment="用户名"),
                    Column("created_at", "timestamp", default="CURRENT_TIMESTAMP"),
                    Column("updated_at", "timestamp", default="CURRENT_TIMESTAMP"),
                ],
                indexes=["idx_users_email", "idx_users_created_at"]
            ),
            Table(
                name="auth_tokens",
                columns=[
                    Column("id", "uuid", primary_key=True),
                    Column("user_id", "uuid", foreign_key="users.id", comment="用户 ID"),
                    Column("token", "varchar(500)", unique=True, comment="Token"),
                    Column("expires_at", "timestamp", comment="过期时间"),
                    Column("created_at", "timestamp", default="CURRENT_TIMESTAMP"),
                ],
                indexes=["idx_auth_tokens_user_id", "idx_auth_tokens_token"]
            ),
        ]

    def _generate_prisma_migration(self) -> dict[str, str]:
        """生成 Prisma 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # schema.prisma
        schema_lines = [
            "// This is your Prisma schema file,",
            "// learn more about it in the docs: https://pris.ly/d/prisma-schema",
            "",
            f'generator client {{',
            '  provider = "prisma-client-js"',
            '}',
            "",
            f'datasource db {{',
            f'  provider = "{self._get_prisma_provider()}"',
            '  url      = env("DATABASE_URL")',
            '}',
            "",
        ]

        # 添加模型
        for entity in self.entities:
            schema_lines.append(f'model {entity.name.capitalize()} {{')
            for col in entity.columns:
                schema_lines.append(f'  {col.name} {self._prisma_type(col.type)}'
                                   f'{"" if col.nullable else "?"}')
            schema_lines.append("}")
            schema_lines.append("")

        # migration.sql
        migration_lines = [
            "-- Migration SQL",
            f"-- Created: {datetime.datetime.now().isoformat()}",
            "",
        ]

        for entity in self.entities:
            migration_lines.append(f"-- Create {entity.name} table")
            migration_lines.append(f"CREATE TABLE \"{entity.name}\" (")
            col_defs = []
            for col in entity.columns:
                col_defs.append(f'    "{col.name}" {self._sql_type(col.type)}'
                               f'{"" if col.nullable else " NOT NULL"}'
                               f'{" PRIMARY KEY" if col.primary_key else ""}'
                               f'{" UNIQUE" if col.unique else ""}')
            migration_lines.append(",\n".join(col_defs))
            migration_lines.append(");")
            migration_lines.append("")

        return {
            "prisma/schema.prisma": "\n".join(schema_lines),
            f"prisma/migrations/{timestamp}_init/migration.sql": "\n".join(migration_lines),
        }

    def _generate_typeorm_migration(self) -> dict[str, str]:
        """生成 TypeORM 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        entity_lines = []
        for entity in self.entities:
            entity_lines.extend([
                f"import {{ Entity, PrimaryGeneratedColumn, Column }} from 'typeorm';",
                "",
                f"@Entity()",
                f"export class {entity.name.capitalize()} {{",
            ])

            for col in entity.columns:
                decorator = ""
                if col.primary_key:
                    decorator = "@PrimaryGeneratedColumn('uuid')"
                else:
                    col_type = self._typeorm_type(col.type)
                    decorator = f"@Column({{ type: '{col_type}'{{ nullable: {str(col.nullable).lower()} }} }})"

                entity_lines.append(f"  {decorator}")
                entity_lines.append(f"  {col.name}: {self._typescript_type(col.type)};")

            entity_lines.append("}")
            entity_lines.append("")

        # 迁移文件
        migration_lines = [
            "import { MigrationInterface, QueryRunner, Table } from 'typeorm';",
            "",
            f"export class Init{timestamp} {{",
            f"    name = 'Init{timestamp}';",
            "",
            "    public async up(queryRunner: QueryRunner): Promise<void> {",
            "",
        ]

        for entity in self.entities:
            migration_lines.append(f"        // Create {entity.name} table")
            migration_lines.append(f"        await queryRunner.createTable(new Table({{")
            migration_lines.append(f"            name: '{entity.name}',")
            migration_lines.append("            columns: [")

            for col in entity.columns:
                migration_lines.append(f"                {{")
                migration_lines.append(f"                    name: '{col.name}',")
                migration_lines.append(f"                    type: '{self._sql_type(col.type)}',")
                migration_lines.append(f"                    isPrimary: {str(col.primary_key).lower()},")
                migration_lines.append(f"                    isNullable: {str(col.nullable).lower()},")
                migration_lines.append(f"                    isUnique: {str(col.unique).lower()},")
                migration_lines.append(f"                }},")

            migration_lines.append("            ],")
            migration_lines.append("        }));")
            migration_lines.append("")

        migration_lines.extend([
            "    }",
            "",
            "    public async down(queryRunner: QueryRunner): Promise<void> {",
            "",
        ])

        for entity in self.entities:
            migration_lines.append(f"        await queryRunner.dropTable('{entity.name}');")

        migration_lines.extend([
            "",
            "    }",
            "}",
        ])

        return {
            f"src/migrations/{timestamp}_Init.ts": "\n".join(entity_lines + ["", ""] + migration_lines),
        }

    def _generate_sqlalchemy_migration(self) -> dict[str, str]:
        """生成 SQLAlchemy 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # models.py
        models_lines = [
            'from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, create_engine',
            'from sqlalchemy.ext.declarative import declarative_base',
            'from sqlalchemy.orm import sessionmaker, relationship',
            'import uuid',
            "",
            "Base = declarative_base()",
            "",
        ]

        for entity in self.entities:
            models_lines.append(f'class {entity.name.capitalize()}(Base):')
            models_lines.append(f'    __tablename__ = "{entity.name}"')
            models_lines.append("")

            for col in entity.columns:
                py_type = self._python_sqlalchemy_type(col.type)
                nullable = f"nullable={col.nullable}"
                primary_key = f"primary_key={col.primary_key}"
                unique = f"unique={col.unique}" if col.unique else ""
                default_arg = f"default={col.default}" if col.default else ""

                models_lines.append(f'    {col.name} = Column({py_type}, {nullable}, {primary_key}, {unique}, {default_arg})'.replace(", True, ", ", ").replace(", False, ", ", ").replace(", )", ")"))

            models_lines.append("")
            models_lines.append("")

        # alembic 迁移
        migration_lines = [
            '"""Initial migration',
            "",
            f'Revision: {timestamp}',
            'Create Date: ' + datetime.datetime.now().isoformat() + '',
            '"""',
            "from alembic import op",
            "import sqlalchemy as sa",
            "",
            "",
            "def upgrade():",
            "",
        ]

        for entity in self.entities:
            migration_lines.append(f'    op.create_table(')
            migration_lines.append(f'        "{entity.name}",')
            migration_lines.append("        sa.Column(")

            for i, col in enumerate(entity.columns):
                col_type = self._sqlalchemy_type(col.type)
                migration_lines.append(f'            "{col.name}", {col_type}, ')
                migration_lines.append(f'            nullable={col.nullable}, ')
                migration_lines.append(f'            primary_key={col.primary_key}, ')
                if i < len(entity.columns) - 1:
                    migration_lines.append("        ),")
                else:
                    migration_lines.append("        ),")
            migration_lines.append("    )")
            migration_lines.append("")

        migration_lines.extend([
            "",
            "def downgrade():",
            "",
        ])

        for entity in self.entities:
            migration_lines.append(f'    op.drop_table("{entity.name}")')

        return {
            "src/models/__init__.py": "\n".join(models_lines),
            f"alembic/versions/{timestamp}_initial_migration.py": "\n".join(migration_lines),
        }

    def _generate_django_migration(self) -> dict[str, str]:
        """生成 Django 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%d%m%H%M%S")

        # models.py
        models_lines = [
            "from django.db import models",
            "import uuid",
            "",
            "",
        ]

        for entity in self.entities:
            models_lines.append(f'class {entity.name.capitalize()}(models.Model):')
            models_lines.append(f'    """{entity.comment or entity.name}"""')
            models_lines.append("")

            for col in entity.columns:
                field_type = self._django_field_type(col.type)
                nullable = f"null={col.nullable}, " if col.nullable else ""
                unique = f"unique={col.unique}, " if col.unique else ""
                default = f'default="{col.default}", ' if col.default else ""

                if col.primary_key:
                    models_lines.append(f'    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)')
                else:
                    models_lines.append(f'    {col.name} = models.{field_type}({nullable}{unique}{default})')

            models_lines.append("")
            models_lines.append("    class Meta:")
            models_lines.append(f'        db_table = "{entity.name}"')
            models_lines.append("")
            models_lines.append("")

        # Django 迁移文件
        migration_lines = [
            "# Generated by Django",
            f"from django.db import migrations, models",
            f"import django.db.models.deletion",
            f"import uuid",
            "",
            "",
            f"class Migration(migrations.Migration):",
            "",
            f'    initial = True',
            "",
            f'    dependencies = [',
            f'    ]',
            "",
            f'    operations = [',
        ]

        for entity in self.entities:
            migration_lines.append(f'        migrations.CreateModel(')
            migration_lines.append(f'            name=\'{entity.name.capitalize()}\',')
            migration_lines.append(f'            fields=[')

            for col in entity.columns:
                field_def = self._django_migration_field(col)
                migration_lines.append(f'                {field_def},')

            migration_lines.append('            ],')
            migration_lines.append('        ),')

        migration_lines.append('    ]')

        return {
            "src/models.py": "\n".join(models_lines),
            f"src/migrations/{timestamp}_initial.py": "\n".join(migration_lines),
        }

    def _generate_sequelize_migration(self) -> dict[str, str]:
        """生成 Sequelize 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # models
        models_lines = []
        for entity in self.entities:
            models_lines.extend([
                f"module.exports = (sequelize, DataTypes) => {{",
                f"  const {entity.name.capitalize()} = sequelize.define('{entity.name}', {{",
            ])

            for col in entity.columns:
                sequelize_type = self._sequelize_type(col.type)
                models_lines.append(f"    {col.name}: {{")
                models_lines.append(f"      type: DataTypes.{sequelize_type},")
                models_lines.append(f"      allowNull: {str(col.nullable).lower()},")
                models_lines.append(f"      unique: {str(col.unique).lower()},")
                models_lines.append(f"      primaryKey: {str(col.primary_key).lower()},")
                models_lines.append(f"    }},")

            models_lines.extend([
                "  }, {",
                f"    tableName: '{entity.name}',",
                "    timestamps: true,",
                "  });",
                "  return {entity.name.capitalize()};",
                "};",
                "",
            ])

        # migration
        migration_lines = [
            "'use strict';",
            "",
            "module.exports = {",
            "  up: async (queryInterface, Sequelize) => {",
            "",
        ]

        for entity in self.entities:
            migration_lines.extend([
                f'    await queryInterface.createTable("{entity.name}", {{',
            ])

            for col in entity.columns:
                col_type = self._sequelize_type(col.type)
                migration_lines.extend([
                    f'      {col.name}: {{',
                    f'        type: Sequelize.{col_type},',
                    f'        allowNull: {str(col.nullable).lower()},',
                    f'        unique: {str(col.unique).lower()},',
                    f'        primaryKey: {str(col.primary_key).lower()},',
                    f'      }},',
                ])

            migration_lines.extend([
                "    });",
                "",
            ])

        migration_lines.extend([
            "  },",
            "",
            "  down: async (queryInterface, Sequelize) => {",
            "",
        ])

        for entity in self.entities:
            migration_lines.append(f'    await queryInterface.dropTable("{entity.name}");')

        migration_lines.extend([
            "",
            "  },",
            "};",
        ])

        return {
            f"src/models/{timestamp}-create-{self.name}.js": "\n".join(models_lines + ["", ""] + migration_lines),
        }

    def _generate_mongoose_migration(self) -> dict[str, str]:
        """生成 Mongoose 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        models_lines = []
        for entity in self.entities:
            models_lines.extend([
                "const mongoose = require('mongoose');",
                "",
                f"const {entity.name.capitalize()}Schema = new mongoose.Schema({{" if entity.name == self.entities[0].name else f"const {entity.name.capitalize()}Schema = new mongoose.Schema({{",
            ])

            for col in entity.columns:
                mongoose_type = self._mongoose_type(col.type)
                required = "true" if not col.nullable else "false"
                unique = "true" if col.unique else "false"

                models_lines.extend([
                    f"  {col.name}: {{",
                    f"    type: {mongoose_type},",
                    f"    required: {required},",
                    f"    unique: {unique},",
                    f"  }},",
                ])

            models_lines.extend([
                "}, {",
                f"  timestamps: true,",
                f"  collection: '{entity.name}',",
                f"}});",
                "",
                f"module.exports = mongoose.model('{entity.name.capitalize()}', {entity.name.capitalize()}Schema);",
                "",
            ])

        return {
            f"src/models/{entity.name}.model.js": "\n".join(models_lines),
        }

    def _generate_sql_migration(self) -> dict[str, str]:
        """生成原生 SQL 迁移"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # up migration
        up_lines = [
            f"-- Migration Up: {timestamp}",
            f"-- Created: {datetime.datetime.now().isoformat()}",
            "",
        ]

        for entity in self.entities:
            up_lines.extend([
                f"-- Create {entity.name} table",
                f"CREATE TABLE IF NOT EXISTS {entity.name} (",
            ])

            col_defs = []
            for col in entity.columns:
                col_defs.append(f"    {col.name} {self._sql_type(col.type)}"
                               f"{'' if col.nullable else ' NOT NULL'}"
                               f"{' PRIMARY KEY' if col.primary_key else ''}"
                               f"{' UNIQUE' if col.unique else ''}"
                               f"{',' if col != entity.columns[-1] else ''}")

            up_lines.extend(col_defs)
            up_lines.extend([
                ");",
                "",
            ])

        # down migration
        down_lines = [
            f"-- Migration Down: {timestamp}",
            "",
        ]

        for entity in self.entities:
            down_lines.append(f"DROP TABLE IF EXISTS {entity.name} CASCADE;")

        return {
            f"migrations/{timestamp}_up.sql": "\n".join(up_lines),
            f"migrations/{timestamp}_down.sql": "\n".join(down_lines),
        }

    # ==================== 类型转换方法 ====================

    def _get_prisma_provider(self) -> str:
        """获取 Prisma 数据库提供者"""
        providers = {
            DatabaseType.POSTGRESQL: "postgresql",
            DatabaseType.MYSQL: "mysql",
            DatabaseType.SQLITE: "sqlite",
            DatabaseType.MONGODB: "mongodb",
        }
        return providers.get(self.db_type, "postgresql")

    def _prisma_type(self, col_type: str) -> str:
        """转换为 Prisma 类型"""
        type_map = {
            "uuid": "String",
            "varchar": "String",
            "string": "String",
            "text": "String",
            "int": "Int",
            "integer": "Int",
            "bigint": "BigInt",
            "float": "Float",
            "double": "Float",
            "decimal": "Decimal",
            "boolean": "Boolean",
            "bool": "Boolean",
            "date": "DateTime",
            "datetime": "DateTime",
            "timestamp": "DateTime",
            "json": "Json",
            "bytes": "Bytes",
        }
        return type_map.get(col_type.lower().split("(")[0], "String")

    def _sql_type(self, col_type: str) -> str:
        """转换为 SQL 类型"""
        type_map = {
            "uuid": "UUID",
            "varchar": "VARCHAR(255)",
            "string": "VARCHAR(255)",
            "text": "TEXT",
            "int": "INTEGER",
            "integer": "INTEGER",
            "bigint": "BIGINT",
            "float": "FLOAT",
            "double": "DOUBLE PRECISION",
            "decimal": "DECIMAL(10, 2)",
            "boolean": "BOOLEAN",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "TIMESTAMP",
            "timestamp": "TIMESTAMP",
            "json": "JSONB",
            "bytes": "BYTEA",
        }
        return type_map.get(col_type.lower().split("(")[0], "VARCHAR(255)")

    def _typescript_type(self, col_type: str) -> str:
        """转换为 TypeScript 类型"""
        type_map = {
            "uuid": "string",
            "varchar": "string",
            "string": "string",
            "text": "string",
            "int": "number",
            "integer": "number",
            "bigint": "number",
            "float": "number",
            "double": "number",
            "decimal": "number",
            "boolean": "boolean",
            "bool": "boolean",
            "date": "Date",
            "datetime": "Date",
            "timestamp": "Date",
            "json": "object",
            "bytes": "Buffer",
        }
        return type_map.get(col_type.lower().split("(")[0], "any")

    def _typeorm_type(self, col_type: str) -> str:
        """转换为 TypeORM 类型"""
        return self._sql_type(col_type)

    def _python_sqlalchemy_type(self, col_type: str) -> str:
        """转换为 Python SQLAlchemy 类型"""
        type_map = {
            "uuid": "String(36)",
            "varchar": "String",
            "string": "String",
            "text": "Text",
            "int": "Integer",
            "integer": "Integer",
            "bigint": "BigInteger",
            "float": "Float",
            "double": "Float",
            "decimal": "Numeric(10, 2)",
            "boolean": "Boolean",
            "bool": "Boolean",
            "date": "Date",
            "datetime": "DateTime",
            "timestamp": "DateTime",
            "json": "JSON",
            "bytes": "LargeBinary",
        }
        return type_map.get(col_type.lower().split("(")[0], "String")

    def _sqlalchemy_type(self, col_type: str) -> str:
        """转换为 SQLAlchemy Column 类型"""
        type_map = {
            "uuid": "sa.String(36)",
            "varchar": "sa.String",
            "string": "sa.String",
            "text": "sa.Text",
            "int": "sa.Integer",
            "integer": "sa.Integer",
            "bigint": "sa.BigInteger",
            "float": "sa.Float",
            "double": "sa.Float",
            "decimal": "sa.Numeric(10, 2)",
            "boolean": "sa.Boolean",
            "bool": "sa.Boolean",
            "date": "sa.Date",
            "datetime": "sa.DateTime",
            "timestamp": "sa.DateTime",
            "json": "sa.JSON",
            "bytes": "sa.LargeBinary",
        }
        return type_map.get(col_type.lower().split("(")[0], "sa.String")

    def _django_field_type(self, col_type: str) -> str:
        """转换为 Django Field 类型"""
        type_map = {
            "uuid": "UUIDField",
            "varchar": "CharField",
            "string": "CharField",
            "text": "TextField",
            "int": "IntegerField",
            "integer": "IntegerField",
            "bigint": "BigIntegerField",
            "float": "FloatField",
            "double": "FloatField",
            "decimal": "DecimalField",
            "boolean": "BooleanField",
            "bool": "BooleanField",
            "date": "DateField",
            "datetime": "DateTimeField",
            "timestamp": "DateTimeField",
            "json": "JSONField",
            "bytes": "BinaryField",
        }
        return type_map.get(col_type.lower().split("(")[0], "CharField")

    def _django_migration_field(self, col: Column) -> str:
        """生成 Django 迁移字段定义"""
        field_type = self._django_field_type(col.type)
        args = []

        if col.primary_key:
            return f"models.UUIDField(primary_key=True, default=uuid.uuid4)"

        if not col.nullable:
            args.append("null=False")

        if col.unique:
            args.append("unique=True")

        if col.default:
            args.append(f'default="{col.default}"')

        # 根据类型添加 max_length
        if field_type in ["CharField", "UUIDField"]:
            args.append("max_length=255")

        args_str = ", ".join(args) if args else ""
        return f'models.{field_type}({args_str})'

    def _sequelize_type(self, col_type: str) -> str:
        """转换为 Sequelize 类型"""
        type_map = {
            "uuid": "UUID",
            "varchar": "STRING",
            "string": "STRING",
            "text": "TEXT",
            "int": "INTEGER",
            "integer": "INTEGER",
            "bigint": "BIGINT",
            "float": "FLOAT",
            "double": "DOUBLE",
            "decimal": "DECIMAL(10, 2)",
            "boolean": "BOOLEAN",
            "bool": "BOOLEAN",
            "date": "DATE",
            "datetime": "DATE",
            "timestamp": "DATE",
            "json": "JSON",
            "bytes": "BLOB",
        }
        return type_map.get(col_type.lower().split("(")[0], "STRING")

    def _mongoose_type(self, col_type: str) -> str:
        """转换为 Mongoose 类型"""
        type_map = {
            "uuid": "Schema.Types.UUID",
            "varchar": "String",
            "string": "String",
            "text": "String",
            "int": "Number",
            "integer": "Number",
            "bigint": "Schema.Types.Long",
            "float": "Number",
            "double": "Number",
            "decimal": "Schema.Types.Decimal128",
            "boolean": "Boolean",
            "bool": "Boolean",
            "date": "Date",
            "datetime": "Date",
            "timestamp": "Date",
            "json": "Schema.Types.Mixed",
            "bytes": "Buffer",
        }
        return type_map.get(col_type.lower().split("(")[0], "String")
