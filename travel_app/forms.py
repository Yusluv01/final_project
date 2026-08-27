from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password

from .models import (
    Client,
    Booking,
    Document,
    Payment,
    Message,
    ClientDocument,
    Agent,
    AgentInvitation,
)

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'passport_number', 'passport_expiry',
            'nationality', 'date_of_birth', 'email', 'phone', 'address',
            'travel_type'
        ]
        widgets = {
            'passport_expiry': forms.DateInput(attrs={'type': 'date'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_passport_number(self):
        passport = self.cleaned_data.get('passport_number')
        if not passport:
            return passport
            
        # ✅ FIX: If editing, exclude this current client from the uniqueness check
        if self.instance and self.instance.pk:
            if Client.objects.filter(passport_number=passport).exclude(pk=self.instance.pk).exists():
                raise ValidationError('A client with this passport number already exists.')
        else:
            # For new clients, just check the whole database
            if Client.objects.filter(passport_number=passport).exists():
                raise ValidationError('A client with this passport number already exists.')
                
        return passport

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'client', 'package', 'status', 'total_amount', 'travel_date_start',
            'travel_date_end', 'special_requests'
        ]
        widgets = {
            'travel_date_start': forms.DateInput(attrs={'type': 'date'}),
            'travel_date_end': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
        }


class ClientDocumentUploadForm(forms.ModelForm):
    """
    Form used by clients to upload travel documents.

    Allowed file formats:
    - PDF
    - JPG
    - JPEG
    - PNG
    - WEBP

    Maximum file size:
    - 10 MB
    """

    class Meta:
        model = ClientDocument

        fields = [
            'document_type',
            'file',
        ]

        widgets = {

            'document_type': forms.Select(
                attrs={
                    'class': (
                        'w-full px-3 py-2 border '
                        'border-gray-300 rounded-lg '
                        'focus:ring-2 focus:ring-blue-500 '
                        'focus:border-blue-500 '
                        'outline-none'
                    )
                }
            ),

            'file': forms.FileInput(
                attrs={
                    'class': (
                        'w-full px-3 py-2 border '
                        'border-gray-300 rounded-lg '
                        'focus:ring-2 focus:ring-blue-500 '
                        'focus:border-blue-500 '
                        'outline-none'
                    ),

                    # Browser file picker will only show
                    # these supported document formats.
                    'accept': '.pdf,.jpg,.jpeg,.png,.webp',

                }
            ),
        }


    def clean_file(self):
        """
        Validate the uploaded document before saving it.
        """

        uploaded_file = self.cleaned_data.get('file')


        # ============================================================
        # CHECK 1: FILE EXISTS
        # ============================================================

        if not uploaded_file:

            raise forms.ValidationError(
                'Please select a document to upload.'
            )


        # ============================================================
        # CHECK 2: FILE SIZE
        # Maximum allowed size = 10 MB
        # ============================================================

        max_size = 10 * 1024 * 1024

        if uploaded_file.size > max_size:

            raise forms.ValidationError(
                'File size must not exceed 10 MB.'
            )


        # ============================================================
        # CHECK 3: FILE EXTENSION
        # ============================================================

        allowed_extensions = {
            '.pdf',
            '.jpg',
            '.jpeg',
            '.png',
            '.webp',
        }

        file_name = uploaded_file.name.lower()


        # Get the extension from the filename

        import os

        file_extension = os.path.splitext(file_name)[1]


        if file_extension not in allowed_extensions:

            raise forms.ValidationError(
                'Invalid document format. '
                'Please upload PDF, JPG, JPEG, PNG, or WEBP files only.'
            )


        # ============================================================
        # CHECK 4: BLOCK HTML FILES EXPLICITLY
        # ============================================================

        blocked_extensions = {
            '.htm',
            '.html',
            '.php',
            '.exe',
            '.js',
            '.bat',
            '.cmd',
            '.svg',
        }

        if file_extension in blocked_extensions:

            raise forms.ValidationError(
                'This file type is not allowed. '
                'Please upload a genuine PDF or image document.'
            )


        # ============================================================
        # CHECK 5: VERIFY CONTENT TYPE
        # ============================================================

        allowed_content_types = {
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/webp',
        }

        content_type = getattr(
            uploaded_file,
            'content_type',
            ''
        )


        if content_type and content_type not in allowed_content_types:

            raise forms.ValidationError(
                'The uploaded file does not appear to be a valid '
                'PDF or image document.'
            )


        # ============================================================
        # FILE PASSED ALL VALIDATION
        # ============================================================

        return uploaded_file

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content', 'message_type']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


# ==================== CLIENT REGISTRATION FORM ====================
class ClientRegistrationForm(UserCreationForm):
    """Create a client using the project's AUTH_USER_MODEL (Agent)."""
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    passport_number = forms.CharField(max_length=50)

    class Meta:
        model = Agent
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'passport_number', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password2:
            raise ValidationError('Please enter the password confirmation.')
        if password1 and password1 != password2:
            raise ValidationError('The two password fields did not match.')
        try:
            password_validation.validate_password(password2, self.instance)
        except ValidationError as exc:
            # Keep Django's security validators, but expose their messages clearly
            # on the registration form instead of returning only a generic error.
            raise ValidationError(exc.messages)
        return password2

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Client.objects.filter(email__iexact=email).exists():
            raise ValidationError('A client with this email address already exists.')
        if Agent.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email address already exists.')
        return email

    def clean_passport_number(self):
        passport = self.cleaned_data['passport_number'].strip()
        if Client.objects.filter(passport_number__iexact=passport).exists():
            raise ValidationError('A client with this passport number already exists.')
        if Agent.objects.filter(passport_number__iexact=passport).exists():
            raise ValidationError('An account with this passport number already exists.')
        return passport

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        user.is_staff = False
        user.is_superuser = False
        user.phone = self.cleaned_data.get('phone') or None
        user.passport_number = self.cleaned_data.get('passport_number') or None
        if commit:
            user.save()
        return user


# # ==================== CLIENT DOCUMENT UPLOAD FORM ====================
# class ClientDocumentUploadForm(forms.ModelForm):

#     class Meta:
#         model = ClientDocument

#         fields = [
#             'document_type',
#             'file',
#         ]

#         widgets = {
#             'document_type': forms.Select(
#                 attrs={
#                     'class': (
#                         'w-full px-3 py-2 border border-gray-300 '
#                         'rounded-lg focus:ring-2 focus:ring-blue-500'
#                     )
#                 }
#             ),

#             'file': forms.FileInput(
#                 attrs={
#                     'class': (
#                         'w-full px-3 py-2 border border-gray-300 '
#                         'rounded-lg focus:ring-2 focus:ring-blue-500'
#                     ),

#                     # This also helps the browser show appropriate
#                     # files in the file picker.
#                     'accept': '.pdf,.jpg,.jpeg,.png,.webp',
#                 }
#             ),
#         }

#     def clean_file(self):
#         uploaded_file = self.cleaned_data.get('file')

#         if not uploaded_file:
#             raise forms.ValidationError(
#                 'Please select a document to upload.'
#             )

#         # -------------------------------------------------
#         # ALLOWED FILE EXTENSIONS
#         # -------------------------------------------------

#         allowed_extensions = {
#             '.pdf',
#             '.jpg',
#             '.jpeg',
#             '.png',
#             '.webp',
#         }

#         file_name = uploaded_file.name.lower()

#         if '.' not in file_name:
#             raise forms.ValidationError(
#                 'Invalid file. The document must have a valid file extension.'
#             )

#         extension = '.' + file_name.rsplit('.', 1)[1]

#         if extension not in allowed_extensions:
#             raise forms.ValidationError(
#                 'Invalid document format. '
#                 'Please upload a PDF, JPG, JPEG, PNG, or WEBP file.'
#             )

#         # -------------------------------------------------
#         # FILE SIZE LIMIT
#         # -------------------------------------------------

#         max_size = 10 * 1024 * 1024  # 10 MB

#         if uploaded_file.size > max_size:
#             raise forms.ValidationError(
#                 'File is too large. The maximum allowed size is 10 MB.'
#             )

#         # -------------------------------------------------
#         # REJECT HTML FILES EXPLICITLY
#         # -------------------------------------------------

#         if extension in {'.html', '.htm'}:
#             raise forms.ValidationError(
#                 'HTML webpage files are not accepted. '
#                 'Please upload the actual document as a PDF or image.'
#             )

#         # -------------------------------------------------
#         # BASIC CONTENT-TYPE CHECK
#         # -------------------------------------------------

#         content_type = getattr(
#             uploaded_file,
#             'content_type',
#             ''
#         ).lower()

#         allowed_content_types = {
#             'application/pdf',
#             'image/jpeg',
#             'image/png',
#             'image/webp',
#         }

#         if content_type and content_type not in allowed_content_types:
#             raise forms.ValidationError(
#                 'The uploaded file does not appear to be a valid '
#                 'PDF or image document.'
#             )

#         return uploaded_file


class AgentRegistrationForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'First name'
            }
        )
    )

    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Last name'
            }
        )
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Email address'
            }
        )
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Phone number'
            }
        )
    )

    nationality = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Nationality'
            }
        )
    )

    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                )
            }
        )
    )

    next_of_kin_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Next of kin phone number'
            }
        )
    )

    class Meta:
        model = Agent
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'nationality',
            'date_of_birth',
            'next_of_kin_phone',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if Agent.objects.filter(
            email__iexact=email
        ).exists():
            raise ValidationError(
                'An account with this email address already exists.'
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone') or None

        user.nationality = self.cleaned_data['nationality']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        user.next_of_kin_phone = self.cleaned_data['next_of_kin_phone']

        # AGENT/STAFF ACCOUNT
        user.role = 'staff'
        user.is_staff = True
        user.is_superuser = False

        if commit:
            user.save()

        return user


# ============================================================
# AGENT INVITATION FORMS
# ============================================================

class AgentInvitationForm(forms.ModelForm):
    """
    Form used by an administrator to invite a new
    Admin or Staff member.
    """

    class Meta:
        model = AgentInvitation
        fields = ['email', 'role']

        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': (
                        'w-full px-4 py-3 border border-gray-300 '
                        'rounded-lg focus:ring-2 focus:ring-blue-500 '
                        'focus:border-blue-500 outline-none'
                    ),
                    'placeholder': 'Email address',
                }
            ),

            'role': forms.Select(
                attrs={
                    'class': (
                        'w-full px-4 py-3 border border-gray-300 '
                        'rounded-lg focus:ring-2 focus:ring-blue-500 '
                        'focus:border-blue-500 outline-none'
                    ),
                }
            ),
        }
        
def clean_email(self):
    email = self.cleaned_data['email'].strip().lower()

    if Agent.objects.filter(
        email__iexact=email
    ).exists():
        raise ValidationError(
            'An account with this email address already exists.'
        )

        if AgentInvitation.objects.filter(
    email__iexact=email,
    is_accepted=False,
    expires_at__gt=timezone.now(),
).exists():
    raise ValidationError(
        'There is already an active invitation for this email address.'
    )        
    return email


class AcceptAgentInvitationForm(forms.Form):
    """
    Form used by an invited Admin/Staff member to
    complete their account setup.
    """

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Username',
            }
        )
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'First name',
            }
        )
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Last name',
            }
        )
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Phone number',
            }
        )
    )

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Password',
            }
        )
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                'class': (
                    'w-full px-4 py-3 border border-gray-300 '
                    'rounded-lg focus:ring-2 focus:ring-blue-500 '
                    'focus:border-blue-500 outline-none'
                ),
                'placeholder': 'Confirm password',
            }
        )
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()

        if Agent.objects.filter(
            username__iexact=username
        ).exists():
            raise ValidationError(
                'This username is already taken.'
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                'The passwords do not match.'
            )

        if password1:
            validate_password(password1)

        return cleaned_data
