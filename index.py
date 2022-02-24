from flask import Flask, render_template, request, make_response, json, send_from_directory
import datetime
import coordtransform
import pandas as pd
app = Flask('__name__')
app.config['coordFilePath'] = './static/coordFiles/'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/point', methods=['GET'])
def point():
    type = request.args.get('type')
    srcx = float(request.args.get('x'))
    srcy = float(request.args.get('y'))
    if int(type):
        dstx, dsty = coordtransform.sh_to_wgs84(srcx, srcy)
    else:
        dstx, dsty = coordtransform.wgs84_to_sh(srcx, srcy)
    data = {

        'x': dstx,
        'y': dsty
    }
    return make_response(json.dumps(data))


@app.route('/batch', methods=['POST'])
def batch():
    type = int(request.form.get('type'))
    file = request.files.get('file')
    fileName = int(datetime.datetime.now().timestamp()*pow(10, 6))
    file.save('{}{}.csv'.format(app.config['coordFilePath'],fileName))
    srcCoordDf = pd.read_csv('{}{}.csv'.format(app.config['coordFilePath'],fileName), header=0)
    srcCoords = srcCoordDf.values
    dstCoords = list()
    N = srcCoords.shape[0]
    if not(type):
        for i in range(N):
            lon = srcCoords[i, 0]
            lat = srcCoords[i, 1]
            x, y = coordtransform.wgs84_to_sh(lon, lat)
            dstCoords.append([x, y])
        dstCoordDf = pd.DataFrame(dstCoords, columns=['x', 'y'])
        dstCoordDf.to_csv('{}{}_.csv'.format(app.config['coordFilePath'],fileName), index=False)
    else:
        for i in range(N):
            x = srcCoords[i, 0]
            y = srcCoords[i, 1]
            lon, lat = coordtransform.sh_to_wgs84(x, y)
            dstCoords.append([lon, lat])
        dstCoordDf = pd.DataFrame(dstCoords, columns=['longitude', 'latitude'])
        dstCoordDf.to_csv('{}{}_.csv'.format(app.config['coordFilePath'],fileName), index=False)
    return send_from_directory(app.config['coordFilePath'],f'{fileName}_.csv',as_attachment=True)


if __name__ == '__main__':
    app.run()
