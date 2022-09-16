/** @odoo-module **/

import MrpDocumentsControllerMixin from '@mrp/js/mrp_documents_controller_mixin';

/**
 * @override
*/
MrpDocumentsControllerMixin._onClickMrpDocumentsUpload = function _onClickMrpDocumentsUpload() {
    const $uploadInput = $('<input>', {
        type: 'file',
        name: 'files[]',
        multiple: 'multiple'
    });
    $uploadInput.on('change', async ev => {
        var allow_to_upload = 1
        if (this.modelName == "mrp.document"){
            for (let i = 0; i < ev.target.files.length; i++) {
                let file = ev.target.files.item(i);
                if (file.type.indexOf('pdf') == -1){
                    allow_to_upload = 0
                }
            }
        }
        if (allow_to_upload == 0){
            alert("Only PDF files allowed!")
        }
        if (allow_to_upload == 1){
            await this._uploadFiles(ev.target.files);
        }
        $uploadInput.remove();
    });
    $uploadInput.click();
}