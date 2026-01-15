from django import forms
from .models import UploadedFile


class ExcelUploadForm(forms.ModelForm):
    """Form for uploading Excel files"""
    
    skip_rows = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        max_value=100,
        help_text='Number of rows to skip from the beginning (e.g., 8 to start from row 9)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': '0'
        })
    )
    
    class Meta:
        model = UploadedFile
        fields = ['file_path']
        widgets = {
            'file_path': forms.FileInput(attrs={
                'accept': '.xls,.xlsx',
                'class': 'hidden',
                'id': 'file-upload'
            })
        }
    
    def clean_file_path(self):
        file = self.cleaned_data.get('file_path')
        
        if file:
            # Check file extension
            if not file.name.endswith(('.xls', '.xlsx')):
                raise forms.ValidationError('Only Excel files (.xls, .xlsx) are allowed.')
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
        
        return file
