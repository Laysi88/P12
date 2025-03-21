from view.menu_view import show_menu


def test_show_menu_output(sample_user, capsys):
    """Test que `show_menu()` affiche bien le menu principal sans formatage de Rich."""

    show_menu(sample_user)

    captured = capsys.readouterr()
    output = captured.out

    assert f"🔐 Connecté en tant que {sample_user.name} - {sample_user.role.name}" in output
    assert "=== Menu Principal ===" in output
    assert "1️⃣ Gérer les utilisateurs" in output
    assert "2️⃣ Gérer les clients" in output
    assert "3️⃣ Gérer les contrats" in output
    assert "4️⃣ Gérer les événements" in output
    assert "0️⃣ Quitter" in output
    assert "🔑 Logout (L)" in output
