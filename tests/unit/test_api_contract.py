"""Tests for APIContractGenerator."""

from pathlib import Path

from super_dev.creators.api_contract import APIContractGenerator


class TestAPIContractGenerator:
    def test_generate_shared_types_with_no_content(self, tmp_path: Path):
        gen = APIContractGenerator()
        result = gen.generate_shared_types(tmp_path)

        assert "ApiResponse" in result
        assert "export interface" in result
        assert "API_ROUTES" in result

    def test_generate_shared_types_with_arch_content(self, tmp_path: Path):
        arch = (
            "# Architecture\n\n"
            "## User Model\n"
            "- id: string\n"
            "- email: string\n"
            "- name: string\n"
            "- createdAt: datetime\n"
            "\n"
            "## API Routes\n"
            "GET /api/users\n"
            "GET /api/users/:id\n"
            "POST /api/auth/login\n"
        )
        gen = APIContractGenerator()
        result = gen.generate_shared_types(tmp_path, arch_content=arch)

        assert "export interface User" in result
        assert "id: string;" in result
        assert "email: string;" in result
        assert "createdAt: string;" in result  # datetime maps to string
        assert "API_ROUTES" in result
        assert "USERS" in result

    def test_generate_shared_types_reads_from_file(self, tmp_path: Path):
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        arch_file = output_dir / "demo-architecture.md"
        arch_file.write_text(
            "# Arch\n\n## Product Model\n- id: uuid\n- title: string\n- price: decimal\n\n"
            "GET /api/products\n"
            "POST /api/products\n",
            encoding="utf-8",
        )

        gen = APIContractGenerator()
        result = gen.generate_shared_types(tmp_path)

        assert "export interface Product" in result
        assert "id: string;" in result
        assert "price: number;" in result

    def test_generate_api_client_basic(self, tmp_path: Path):
        gen = APIContractGenerator()
        result = gen.generate_api_client(tmp_path)

        assert "fetchApi" in result
        assert "export const api" in result
        assert "api-client.ts" in result

    def test_generate_api_client_with_routes(self, tmp_path: Path):
        arch = (
            "GET /api/users\n" "GET /api/users/:id\n" "POST /api/users\n" "DELETE /api/users/:id\n"
        )
        gen = APIContractGenerator()
        result = gen.generate_api_client(tmp_path, arch_content=arch)

        assert "fetchApi" in result
        assert "api" in result

    def test_generate_for_project_writes_files(self, tmp_path: Path):
        gen = APIContractGenerator()
        written = gen.generate_for_project(tmp_path)

        assert len(written) == 2
        types_path = tmp_path / "output" / "shared" / "types.ts"
        client_path = tmp_path / "output" / "shared" / "api-client.ts"
        assert types_path.exists()
        assert client_path.exists()

    def test_route_to_const_name(self):
        gen = APIContractGenerator()
        assert gen._route_to_const_name("GET", "/api/users") == "USERS"
        assert gen._route_to_const_name("POST", "/api/users") == "POST_USERS"
        assert gen._route_to_const_name("GET", "/api/users/:id") == "USERS_ID"
        assert gen._route_to_const_name("DELETE", "/api/users/:id") == "DELETE_USERS_ID"

    def test_path_to_ts_static(self):
        gen = APIContractGenerator()
        assert gen._path_to_ts("/api/users") == '"/api/users"'

    def test_path_to_ts_with_params(self):
        gen = APIContractGenerator()
        result = gen._path_to_ts("/api/users/:id")
        assert "id: string" in result
        assert "${id}" in result
        assert "as const" in result

    def test_extract_models_empty(self):
        models = APIContractGenerator._extract_models("")
        assert models == []

    def test_extract_routes_empty(self):
        routes = APIContractGenerator._extract_routes("")
        assert routes == []

    def test_extract_routes_deduplicates(self):
        content = "GET /api/users\nGET /api/users\nPOST /api/users\n"
        routes = APIContractGenerator._extract_routes(content)
        assert len(routes) == 2

    def test_types_file_has_auto_generated_comment(self, tmp_path: Path):
        gen = APIContractGenerator()
        result = gen.generate_shared_types(tmp_path)
        assert "Auto-generated" in result
        assert "super-dev generate types" in result

    def test_api_response_generic_type(self, tmp_path: Path):
        gen = APIContractGenerator()
        result = gen.generate_shared_types(tmp_path)
        assert "ApiResponse<T>" in result
        assert "success: boolean;" in result
        assert "data: T;" in result
        assert "error?: string;" in result
