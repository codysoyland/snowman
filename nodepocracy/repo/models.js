// define your models here!

var wilson = require('wilson'),
    models = wilson.models,
    reverse = wilson.urls.reverse;

exports.Repository = models.model({
    'user_id':models.PositiveIntegerField(),
    'name':models.CharField({'max_length':255}),
    'slug':models.CharField({'max_length':255}),
    'origin':models.CharField({'max_length':255}),
    'fs_path':models.CharField({'max_length':255}),
    'status':models.IntegerField(),
    'claim_hash':models.CharField({'max_length':40}),

    'get_absolute_url':function() {
        return reverse(this._meta.app_name+':repo_detail', [this.slug]); 
    },
    Meta:{
        'ordering':'name'
    }
});
