from django import forms


class Login_Form(forms.Form):
    username = forms.CharField(
        label='用户名',
        min_length=2,
        max_length=30,
        error_messages={
            'min_length':'用户名不得少于2位',
            'max_length':'用户名不得超过30位',
            'required':'不能为空!'
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control"},
        )
    )
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=30,
        error_messages={
            'required':'不能为空！',
            'min_length':'密码不能少于8位',
            'max_length':'密码不能超过30位',
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class':'form-control'},
            render_value=True,
        ),
    )
