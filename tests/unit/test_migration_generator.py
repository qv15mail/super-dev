"""
数据库迁移生成器测试
"""

from pathlib import Path

from super_dev.deployers.migration import MigrationGenerator


class TestMigrationGenerator:
    def test_infer_entities_from_change_specs_modules(self, temp_project_dir: Path):
        spec_file = (
            temp_project_dir
            / ".super-dev"
            / "changes"
            / "add-payment"
            / "specs"
            / "payment"
            / "spec.md"
        )
        spec_file.parent.mkdir(parents=True, exist_ok=True)
        spec_file.write_text("## ADDED Requirements\n", encoding="utf-8")

        generator = MigrationGenerator(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "node"},
        )

        table_names = [table.name for table in generator.entities]
        assert "payments" in table_names
        assert "users" not in table_names

    def test_infer_entities_from_api_contract(self, temp_project_dir: Path):
        api_contract = temp_project_dir / "backend" / "API_CONTRACT.md"
        api_contract.parent.mkdir(parents=True, exist_ok=True)
        api_contract.write_text(
            "# API\n\n- GET /api/order\n- POST /api/order\n",
            encoding="utf-8",
        )

        generator = MigrationGenerator(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "node"},
        )

        table_names = [table.name for table in generator.entities]
        assert "orders" in table_names

    def test_prisma_migration_uses_inferred_module_table(self, temp_project_dir: Path):
        spec_file = (
            temp_project_dir
            / ".super-dev"
            / "changes"
            / "add-booking"
            / "specs"
            / "booking"
            / "spec.md"
        )
        spec_file.parent.mkdir(parents=True, exist_ok=True)
        spec_file.write_text("## ADDED Requirements\n", encoding="utf-8")

        generator = MigrationGenerator(
            project_dir=temp_project_dir,
            name="demo",
            tech_stack={"backend": "node"},
        )
        files = generator.generate()
        schema = files["prisma/schema.prisma"]

        assert "model Bookings" in schema
