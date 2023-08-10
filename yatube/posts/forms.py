from django.forms import ModelForm, TextInput, Textarea

from posts.models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': Textarea(
                attrs={
                    'placeholder': 'Текст поста',
                },
            ),
            'title': TextInput(
                attrs={
                    'placeholder': 'Название группы',
                },
            ),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Текст нового комментария',
        }
