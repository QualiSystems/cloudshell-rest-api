from mock import patch, Mock
from pyfakefs import fake_filesystem_unittest
from requests import Response

from cloudshell.rest.api import PackagingRestApiClient
from cloudshell.rest.exceptions import ShellNotFoundException, FeatureUnavailable


class TestPackagingRestApiClient(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('cloudshell.rest.api.urllib2.build_opener')
    def test_login(self, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener

        # Act
        PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')

        # Assert
        self.assertTrue(mock_opener.open.called, 'open should be called')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.post')
    def test_add_shell(self, mock_post, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.fs.CreateFile('work//NutShell.zip', contents='ZIP CONTENT')
        mock_post.return_value = Response()
        mock_post.return_value.status_code = 201  # Created

        # Act
        client.add_shell('work//NutShell.zip')

        # Assert
        self.assertTrue(mock_post.called, 'Post should be called')
        self.assertEqual(mock_post.call_args[0][0], 'http://SERVER:9000/API/Shells')
        self.assertEqual(mock_post.call_args[1]['headers']['Authorization'], 'Basic TOKEN')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.put')
    def test_update_shell(self, mock_put, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.fs.CreateFile('work//NutShell.zip', contents='ZIP CONTENT')
        mock_put.return_value = Response()
        mock_put.return_value.status_code = 200  # Ok

        # Act
        client.update_shell('work//NutShell.zip')

        # Assert
        self.assertTrue(mock_put.called, 'Post should be called')
        self.assertEqual(mock_put.call_args[0][0], 'http://SERVER:9000/API/Shells/NutShell')
        self.assertEqual(mock_put.call_args[1]['headers']['Authorization'], 'Basic TOKEN')    \

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.put')
    def test_update_shell_name_given(self, mock_put, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.fs.CreateFile('work//NutShell.zip', contents='ZIP CONTENT')
        mock_put.return_value = Response()
        mock_put.return_value.status_code = 200  # Ok

        # Act
        client.update_shell('work//NutShell.zip', 'my_amazing_shell')

        # Assert
        self.assertTrue(mock_put.called, 'Put should be called')
        self.assertEqual(mock_put.call_args[0][0], 'http://SERVER:9000/API/Shells/my_amazing_shell')
        self.assertEqual(mock_put.call_args[1]['headers']['Authorization'], 'Basic TOKEN')    \

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.put')
    def test_update_shell_throws_shell_not_found_exception_when_404_code_returned(self, mock_put, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.fs.CreateFile('work//NutShell.zip', contents='ZIP CONTENT')
        mock_put.return_value = Response()
        mock_put.return_value.status_code = 404  # Not Found

        # Act & Assert
        self.assertRaises(ShellNotFoundException, client.update_shell, 'work//NutShell.zip')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.get')
    def test_get_installed_standards(self, mock_get, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        mock_get.return_value = Response()
        mock_get.return_value._content = "[]"  # hack - empty response content
        mock_get.return_value.status_code = 200  # Ok

        # Act
        client.get_installed_standards()

        # Assert
        self.assertTrue(mock_get.called, 'Get should be called')
        self.assertEqual(mock_get.call_args[0][0], 'http://SERVER:9000/API/Standards')
        self.assertEqual(mock_get.call_args[1]['headers']['Authorization'], 'Basic TOKEN')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.get')
    def test_get_installed_standards_feature_not_install_error_thrown(self, mock_get, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        mock_get.return_value = Response()
        mock_get.return_value.status_code = 404  # Not Found

        # Act Assert
        self.assertRaises(FeatureUnavailable, client.get_installed_standards)

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.get')
    def test_get_shell_success(self, mock_get, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        mock_get.return_value = Response()
        mock_get.return_value._content = "[]"  # hack - empty response content
        mock_get.return_value.status_code = 200  # Ok

        # Act
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        client.get_shell('shell')

        # Assert
        self.assertTrue(mock_get.called, 'Get should be called')
        self.assertEqual(mock_get.call_args[0][0], 'http://SERVER:9000/API/Shells/shell')
        self.assertEqual(mock_get.call_args[1]['headers']['Authorization'], 'Basic TOKEN')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.get')
    def test_get_shell_feature_unavailable_raises_error(self, mock_get, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        mock_get.return_value = Response()
        mock_get.return_value.status_code = 404  # Not Found

        # Act Assert
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.assertRaises(FeatureUnavailable, client.get_shell, 'shell')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.get')
    def test_get_shell_shell_not_found_raises_error(self, mock_get, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        mock_get.return_value = Response()
        mock_get.return_value.status_code = 400  # Bad Request

        # Act Assert
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        self.assertRaises(ShellNotFoundException, client.get_shell, 'shell')

    @patch('cloudshell.rest.api.urllib2.build_opener')
    @patch('cloudshell.rest.api.get')
    def test_get_shell_unexpected_error_raises_error(self, mock_get, mock_build_opener):
        # Arrange
        mock_url = Mock()
        mock_url.read = Mock(return_value='TOKEN')
        mock_opener = Mock()
        mock_opener.open = Mock(return_value=mock_url)
        mock_build_opener.return_value = mock_opener
        response_obj = type('', (Response,), {"text": 'amazing error'})()
        mock_get.return_value = response_obj
        mock_get.return_value.status_code = 405  # Method Not Allowed

        # Act Assert
        client = PackagingRestApiClient('SERVER', 9000, 'USER', 'PASS', 'Global')
        try:
            client.get_shell('shell')
        except Exception as e:
            self.assertEqual(e.message, 'amazing error')
